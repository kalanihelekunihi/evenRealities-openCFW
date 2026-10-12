#!/usr/bin/env python3
"""Check 16-bit ATT write length and packet effects against native 0x4b579c."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_att_requests.c'
STUB='''#include <stdint.h>
void *audio_ble_att_message_allocate_4b50ae(uint16_t n){(void)n;return 0;}
void audio_ble_attc_send_message_4b5640(uint8_t a,uint16_t b,uint8_t c,void*d,uint8_t e){(void)a;(void)b;(void)c;(void)d;(void)e;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'write.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_attc_write_request',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,length,allocate):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  u.mem_write(0x20081000,bytes((i*13+3)&255 for i in range(512)))
  u.mem_write(0x20082000,bytes(512))
  trace=[]
  names=[('alloc','audio_ble_att_message_allocate_4b50ae',0x4b50ae),('copy','audio_queue_copy_bytes',0x439be4),('send','audio_ble_attc_send_message_4b5640',0x4b5640)]
  for name,cname,stock in names:
   addr=(sy[cname]&~1) if compiled else stock
   def hook(uc,pc,size,user,name=name):
    a,b,c,d=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='alloc':trace.append(('alloc',a));uc.reg_write(UC_ARM_REG_R0,0x20082000 if allocate else 0)
    elif name=='copy':trace.append(('copy',c));uc.mem_write(a,bytes(uc.mem_read(b,c)))
    else:trace.append(('send',a,b,c,bytes(uc.mem_read(d,11+length))))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=addr,end=addr)
  for r,v in ((UC_ARM_REG_R0,3),(UC_ARM_REG_R1,0x1234),(UC_ARM_REG_R2,length),(UC_ARM_REG_R3,0x20081000),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  entry=(sy['audio_ble_attc_write_request']&~1) if compiled else 0x4b579c
  u.emu_start(entry|1,0x600000,count=30000)
  return trace
 cases=0
 for length in (0,6,19,64,255,256,257):
  for allocate in (0,1):
   a=run(False,length,allocate);b=run(True,length,allocate)
   assert a==b,(length,allocate,a,b)
   cases+=1
 print('PASS_BLE_ATTC_WRITE_LENGTH_NATIVE',cases)
