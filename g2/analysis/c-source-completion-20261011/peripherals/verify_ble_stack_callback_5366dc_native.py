#!/usr/bin/env python3
"""Actual compiled-C/native key callback copy/send effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_stack_callback_5366dc.c'
STUB='''#include <stdint.h>
void WStrReverseCpy(uint8_t*d,const uint8_t*s,uint16_t n){for(unsigned i=0;i<n;i++)d[i]=s[n-1-i];}
void WsfMsgSend(uint8_t h,void*p){(void)h;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_callback_5366dc',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,opcode,status,seed,handler):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  msg=0x20081000;event=0x20082000;u.mem_write(msg,bytes([0xa5]*80));e=bytearray((seed+i*7)&255 for i in range(80));e[2]=opcode;e[3]=status;u.mem_write(event,bytes(e));trace=[]
  a=(sy['WStrReverseCpy']&~1) if compiled else 0x56d8c4
  def rev(uc,pc,n,user):
   d=uc.reg_read(UC_ARM_REG_R0);s=uc.reg_read(UC_ARM_REG_R1);size=uc.reg_read(UC_ARM_REG_R2)
   trace.append(('reverse',d-msg,s-event,size));uc.mem_write(d,bytes(uc.mem_read(s,size))[::-1]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,rev,begin=a,end=a)
  a=(sy['WsfMsgSend']&~1) if compiled else 0x4bf9ba
  def send(uc,pc,n,user):
   trace.append(('send',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)==msg));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,send,begin=a,end=a)
  for r,v in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),(msg,event,handler)):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_stack_callback_5366dc'] if compiled else 0x5366dc)|1,0x600000,count=4000)
  return bytes(u.mem_read(msg,80)),trace
 cases=0
 for opcode in (0x25,0x26,0x24,0xff):
  for status in (0x12,0x11):
   for seed in (0,1,127):
    for handler in (0,0x78):
     a,b=run(False,opcode,status,seed,handler),run(True,opcode,status,seed,handler)
     assert a==b,(opcode,status,seed,handler,a,b)
     cases+=1
 print('PASS_BLE_STACK_CALLBACK_5366DC_NATIVE',cases)
