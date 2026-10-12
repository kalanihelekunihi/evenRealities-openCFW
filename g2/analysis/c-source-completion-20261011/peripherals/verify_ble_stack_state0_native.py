#!/usr/bin/env python3
"""Actual compiled-C/native state-zero and shift effects, state-one held equal."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_stack_state0_5365a6.c'
STUB='''#include <stdint.h>
void audio_ble_stack_copy16_542a44(void*d,const void*s){uint8_t*x=d;const uint8_t*y=s;for(unsigned i=0;i<16;i++)x[i]=y[i];}
void audio_ble_stack_state1_5364a4(uint8_t*p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_state0_5365a6',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,seed,low):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  msg=0x20081000;ctx=0x20082000;m=bytearray([0xa5]*64);m[0x30:0x34]=ctx.to_bytes(4,'little')
  for i in range(16):m[16+i]=(seed+i*17)&255
  u.mem_write(msg,bytes(m));c=bytearray([0xa5]*48);c[0x26]=low;u.mem_write(ctx,bytes(c));trace=[]
  names=[('copy','audio_ble_stack_copy16_542a44',0x542a44),('next','audio_ble_stack_state1_5364a4',0x5364a4)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    if name=='copy':
     d=uc.reg_read(UC_ARM_REG_R0);s=uc.reg_read(UC_ARM_REG_R1);trace.append(('copy',d-ctx,s-msg));uc.mem_write(d,bytes(uc.mem_read(s,16)))
    else:trace.append(('next',uc.reg_read(UC_ARM_REG_R0)==msg))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,msg);u.reg_write(UC_ARM_REG_R3,0x12345678)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_stack_state0_5365a6'] if compiled else 0x5365a6)|1,0x600000,count=5000)
  return bytes(u.mem_read(ctx,48)),trace,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for seed in (0,1,17,93,127,128,254,255):
  for low in (0,1,0x10,0xff):
   a,b=run(False,seed,low),run(True,seed,low)
   assert a==b,(seed,low,a,b)
   cases+=1
 print('PASS_BLE_STACK_STATE0_NATIVE',cases)
