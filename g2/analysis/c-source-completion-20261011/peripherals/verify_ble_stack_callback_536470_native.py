#!/usr/bin/env python3
"""Actual compiled-C/native 16-byte BLE callback copy and send effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_stack_callback_536470.c'
STUB='''#include <stdint.h>
void *audio_queue_copy_bytes(void*d,const void*s,uint32_t n){uint8_t*x=d;const uint8_t*y=s;for(uint32_t i=0;i<n;i++)x[i]=y[i];return d;}
void WsfMsgSend(uint8_t h,void*p){(void)h;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_callback_536470',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,seed,handler):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  msg=0x20081000;payload=0x20082000;u.mem_write(msg,bytes([0xa5]*40));u.mem_write(payload,bytes((seed+i*13)&255 for i in range(32)))
  trace=[]
  a=(sy['audio_queue_copy_bytes']&~1) if compiled else 0x439be4
  def copy(uc,pc,n,user):
   dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);length=uc.reg_read(UC_ARM_REG_R2)
   trace.append(('copy',dst-msg,src-payload,length))
   uc.mem_write(dst,bytes(uc.mem_read(src,length)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,copy,begin=a,end=a)
  a=(sy['WsfMsgSend']&~1) if compiled else 0x4bf9ba
  def send(uc,pc,n,user):
   trace.append(('send',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)==msg));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,send,begin=a,end=a)
  for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),(msg,payload,handler,0x12345678)):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_stack_callback_536470'] if compiled else 0x536470)|1,0x600000,count=3000)
  return bytes(u.mem_read(msg,40)),trace,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for seed in (0,1,17,93,255):
  for handler in (0,1,0x78,0xff):
   a,b=run(False,seed,handler),run(True,seed,handler)
   assert a==b,(seed,handler,a,b)
   cases+=1
 print('PASS_BLE_STACK_CALLBACK_536470_NATIVE',cases)
