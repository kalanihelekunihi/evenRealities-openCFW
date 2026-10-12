#!/usr/bin/env python3
"""Actual compiled-C/native state-two WSF handoff effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_stack_state2_536608.c'
STUB='''#include <stdint.h>
void WsfMsgSend(uint8_t h,void*p){(void)h;(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_state2_536608',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,handler,word):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  msg=0x20081000;ctx=0x20082000;m=bytearray([0xa5]*64);m[0x30:0x34]=ctx.to_bytes(4,'little');u.mem_write(msg,bytes(m))
  c=bytearray(48);c[:4]=word.to_bytes(4,'little');c[40]=handler;u.mem_write(ctx,bytes(c));trace=[]
  a=(sy['WsfMsgSend']&~1) if compiled else 0x4bf9ba
  def send(uc,pc,n,user):
   trace.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)==msg));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,send,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,msg);u.reg_write(UC_ARM_REG_R7,0x12345678)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_stack_state2_536608'] if compiled else 0x536608)|1,0x600000,count=1000)
  return bytes(u.mem_read(msg,64)),trace,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for h in (0,1,0x78,0xff):
  for w in (0,0x12345678,0xffffffff):
   a,b=run(False,h,w),run(True,h,w)
   assert a==b,(h,w,a,b)
   cases+=1
 print('PASS_BLE_STACK_STATE2_NATIVE',cases)
