#!/usr/bin/env python3
"""Actual C/native TPL delayed timeout message and lower effects, logs disabled."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_tpl_timeout_callback.c'
STUB='''#include <stdint.h>
uint8_t audio_ble_controller[0x80];
void *WsfMsgAlloc(uint16_t n){(void)n;return 0;}
void WsfMsgSend(uint8_t h,void*m){(void)h;(void)m;}
void *audio_queue_copy_bytes(void*d,const void*s,uint32_t n){(void)d;(void)s;(void)n;return d;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'tpl.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_tpl_rx_next_packet_timeout',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,handler,allocated,ids):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  cb=sy['audio_ble_controller'] if compiled else 0x200727f0;msg=0x20082000;arg=0x20083000
  u.mem_write(cb+0x56,bytes([handler]));u.mem_write(msg,bytes([0xa5]*20));u.mem_write(arg,bytes(ids));trace=[]
  names=[('get',None,0x4b8122),('flags','audio_log_level',0x43d0ce),('alloc','WsfMsgAlloc',0x4bf99e),('copy','audio_queue_copy_bytes',0x439be4),('send','WsfMsgSend',0x4bf9ba)]
  for name,cs,ns in names:
   if compiled and cs is None:continue
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0,r1,r2=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    if name=='get':uc.reg_write(UC_ARM_REG_R0,cb)
    elif name=='flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,0)
    elif name=='alloc':trace.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,msg if allocated else 0)
    elif name=='copy':trace.append(('copy',r0==msg+12,r1==arg,r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
    else:trace.append(('send',r0,r1==msg))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,arg);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_tpl_rx_next_packet_timeout'] if compiled else 0x4b8c6c)|1,0x600000,count=10000)
  block=bytearray(u.mem_read(msg,20));block[4:8]=b'PTR!' if block[4:8]==struct.pack('<I',msg+12) else block[4:8]
  return trace,bytes(block)
 cases=0
 for handler in (0,1,7):
  for allocated in (0,1):
   for ids in ((1,2,3),(7,8,9),(255,0,42)):
    a,b=run(False,handler,allocated,ids),run(True,handler,allocated,ids)
    assert a==b,(handler,allocated,ids,a,b)
    cases+=1
 print('PASS_TPL_TIMEOUT_CALLBACK_NATIVE',cases)
