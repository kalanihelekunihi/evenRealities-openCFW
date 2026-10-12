#!/usr/bin/env python3
"""First callback dispatch of native/C 20-byte thread-pool queue items."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/worker_thread.c'
SHIM='''#include <stdint.h>
void *audio_uart_pool_queue;
int32_t audio_uart_queue_receive(void*q,void*m,uint32_t p,uint32_t t){(void)q;(void)m;(void)p;(void)t;return -3;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'w.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_worker_thread',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,pre,flags,values):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  q=0x20050000;u.mem_write(sy['audio_uart_pool_queue'] if c else 0x20074aa0,struct.pack('<I',q))
  get=(sy['audio_uart_queue_receive']&~1) if c else 0x449b3c
  logf=(sy['audio_log_flags']&~1) if c else 0x43d0ce
  ext=(sy['audio_log_extended']&~1) if c else 0x43d574
  cmp=(sy['compressed_log_output']&~1) if c else 0x43ce9e
  callback=0x20090000;events=[];idx=[0]
  item=bytearray(20);struct.pack_into('<IIH',item,0,callback|1,values[0],values[3]);struct.pack_into('<II',item,12,values[1],values[2])
  def txt(ptr):return bytes(u.mem_read(ptr,100)).split(b'\0')[0].decode('ascii')
  def hook(uc,addr,size,user):
   if addr==callback:
    events.append(('callback',*[uc.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]));uc.emu_stop();return
   if addr==get:
    i=idx[0];idx[0]+=1
    if i<pre:uc.reg_write(UC_ARM_REG_R0,-3 if i%2==0 else 0);uc.mem_write(uc.reg_read(UC_ARM_REG_R1),b'\0'*20)
    else:uc.mem_write(uc.reg_read(UC_ARM_REG_R1),bytes(item));uc.reg_write(UC_ARM_REG_R0,0)
   elif addr==logf:uc.reg_write(UC_ARM_REG_R0,flags)
   elif addr==ext:
    sp=uc.reg_read(UC_ARM_REG_SP);line,fmt,val=struct.unpack('<III',bytes(uc.mem_read(sp,12)))
    events.append(('ext',line,txt(fmt),val))
   elif addr==cmp:events.append(('compact',uc.reg_read(UC_ARM_REG_R0),txt(uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R3)))
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_uart_worker_thread'] if c else 0x49110c)|1,0,count=100000)
  return events,idx[0]
 cases=0
 for pre in (0,1,2,3):
  for flags in (0,2,5,7):
   values=(0x12345678,0x90010203,0xfeedcafe,0xabcd)
   a=run(False,pre,flags,values);b=run(True,pre,flags,values)
   assert a==b,(pre,flags,a,b)
   cases+=1
 print('PASS_WORKER_THREAD_NATIVE',cases)
