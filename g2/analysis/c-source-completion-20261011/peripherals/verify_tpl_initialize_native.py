#!/usr/bin/env python3
"""Actual compiled-C/native TPL_Init service, context, mutex, and log effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_tpl_initialize.c'
STUB='''#include <stdint.h>
uint8_t audio_tpl_service_table[256*20];
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
void *audio_uart_mutex_new(const void*p){(void)p;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'tpl.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,TPL_Init',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 names={'zero':('audio_uart_buffer_zero',0x43c0e4),'mutex':('audio_uart_mutex_new',0x44971c),'flags':('audio_log_level',0x43d0ce),'ext':('audio_log_extended',0x43d574),'compact':('compressed_log_output',0x43ce9e)}
 def run(compiled,service,existing,created,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  tab=sy['audio_tpl_service_table'] if compiled else 0x20071414
  ctx=sy['audio_tpl_contexts'] if compiled else 0x20070dc8
  cell=sy['audio_tpl_send_mutex'] if compiled else 0x20074b00
  u.mem_write(tab+service*20,bytes([0xa5]*20));u.mem_write(ctx,bytes([0xa5]*224));u.mem_write(cell,struct.pack('<I',existing));trace=[]
  def string(p):return bytes(u.mem_read(p,128)).split(b'\0')[0]
  for name,(cs,ns) in names.items():
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0,r1,r2,r3=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
    if name=='zero':trace.append(('zero',r0==ctx,r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
    elif name=='mutex':trace.append(('mutex',r0));uc.reg_write(UC_ARM_REG_R0,created)
    elif name=='flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,flags)
    elif name=='ext':
     line,msg=struct.unpack('<2I',bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),8)))
     trace.append(('ext',r0,string(r1),string(r2),string(r3),line,string(msg)))
    else:trace.append(('compact',r0,string(r1),string(r2)))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,struct.pack('<I',0x55555555))
  for r,v in ((UC_ARM_REG_R0,service),(UC_ARM_REG_R1,0x11111111),(UC_ARM_REG_R2,0x22222222),(UC_ARM_REG_R3,0x33333333),(UC_ARM_REG_LR,0x600001)):u.reg_write(r,v)
  u.emu_start((sy['TPL_Init'] if compiled else 0x4b892c)|1,0x600000,count=20000)
  out=(u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1))
  if out[1]>=0x100000 and out[1]<0x800000 and out[1]!=0x22222222:out=(out[0],string(out[1]))
  return bytes(u.mem_read(tab+service*20,20)),bytes(u.mem_read(ctx,224)),bytes(u.mem_read(cell,4)),trace,out
 cases=0
 for service in (0,1,3,7):
  for existing in (0,0x20088000):
   for created in (0,0x20089000):
    for flags in (0,1,2,4,7):
     a,b=run(False,service,existing,created,flags),run(True,service,existing,created,flags)
     assert a==b,(service,existing,created,flags,a[-2:],b[-2:])
     cases+=1
 print('PASS_TPL_INITIALIZE_NATIVE',cases)
