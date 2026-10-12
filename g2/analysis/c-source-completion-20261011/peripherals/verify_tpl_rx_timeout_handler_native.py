#!/usr/bin/env python3
"""Actual C/native TPL timeout context lookup and response, logging disabled."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_tpl_rx_timeout_handler.c'
STUB='''#include <stdint.h>
uint8_t audio_tpl_contexts[224];
void tpl_context_free_004b8ba2(uint8_t*p){(void)p;}
void audio_tpl_response(uint8_t p,uint8_t s,uint8_t v,uint8_t c){(void)p;(void)s;(void)v;(void)c;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'tpl.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,TPL_RxPacketTimeoutHandler',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,index,used,match):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_tpl_contexts'] if compiled else 0x20070dc8;data=bytearray(224)
  if index<4:
   row=index*56;data[row]=1 if match else 9;data[row+1]=2;data[row+0x33]=3;data[row+0x30]=used
  u.mem_write(base,bytes(data));ids=0x20083000;u.mem_write(ids,b'\x01\x02\x03');trace=[]
  names=[('flags','audio_log_level',0x43d0ce),('free','tpl_context_free_004b8ba2',0x4b8ba2),('response','audio_tpl_response',0x4b9012)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,0)
    elif name=='free':trace.append(('free',(r0-base)//56))
    else:trace.append(('response',r0,r1,r2,r3))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  for r,v in ((UC_ARM_REG_R0,ids),(UC_ARM_REG_R1,0x2222),(UC_ARM_REG_R2,0x3333),(UC_ARM_REG_R3,0x4444),(UC_ARM_REG_SP,0x200ff000),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  u.emu_start((sy['TPL_RxPacketTimeoutHandler'] if compiled else 0x4b8da2)|1,0x600000,count=10000)
  return trace
 cases=0
 for index in range(5):
  for used in (0,1):
   for match in (0,1):
    a,b=run(False,index,used,match),run(True,index,used,match)
    assert a==b,(index,used,match,a,b)
    cases+=1
 print('PASS_TPL_RX_TIMEOUT_HANDLER_NATIVE',cases)
