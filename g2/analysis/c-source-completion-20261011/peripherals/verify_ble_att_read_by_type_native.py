#!/usr/bin/env python3
"""Compare defined ATT request bytes and child calls in compiled ARM C/stock."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_att_read_by_type.c'
STUB='''#include <stdint.h>
void *audio_ble_hci_msg_data_alloc(uint16_t n,uint8_t p){(void)n;(void)p;return 0;}
void audio_ble_attc_send_message_4b5640(uint8_t a,uint16_t b,uint8_t c,void*d,uint8_t e){(void)a;(void)b;(void)c;(void)d;(void)e;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t n){(void)b;(void)n;return a;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_attc_read_by_type_56c4ee',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for available in (False,True):
  pair=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   u.mem_write(0x20070000,b'\x2a\x2b');u.mem_write(0x20071000,b'\xaa'*32);trace=[]
   for name,cs,stock in (('alloc','audio_ble_hci_msg_data_alloc',0x4bf990),('copy','audio_queue_copy_bytes',0x439be4),('send','audio_ble_attc_send_message_4b5640',0x4b5640)):
    target=sym[cs] if compiled else stock
    def hook(uc,pc,size,user,name=name):
     if name=='alloc':trace.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,0x20071000 if available else 0)
     elif name=='copy':
      dest=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2)
      trace.append((name,dest,src,n));uc.mem_write(dest,bytes(uc.mem_read(src,n)))
     else:
      option=struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4))[0]
      trace.append((name,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),option))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_R0,1);u.reg_write(UC_ARM_REG_R1,1);u.reg_write(UC_ARM_REG_R2,0xffff);u.reg_write(UC_ARM_REG_R3,2)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,struct.pack('<II',0x20070000,0x77));u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_ble_attc_read_by_type_56c4ee'] if compiled else 0x56c4ee)|1,0x600000,count=1000)
   data=bytes(u.mem_read(0x20071000,15));defined=data[:6]+data[8:9]+data[13:15]
   pair.append((trace,defined))
  assert pair[0]==pair[1],(available,pair)
print('PASS_BLE_ATT_READ_BY_TYPE_NATIVE 2')
