#!/usr/bin/env python3
"""Compiled-C/native branch oracle for 0x536620; children held equal."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ble_stack_callback_536620.c'
STUB='''#include <stdint.h>
void audio_ble_stack_copy16_542a44(void*d,const void*s){uint8_t*x=d;const uint8_t*y=s;for(unsigned i=0;i<16;i++)x[i]=y[i];}
void audio_ble_stack_state0_5365a6(uint8_t*p){(void)p;}
void audio_ble_stack_state1_5364a4(uint8_t*p){(void)p;}
void audio_ble_stack_state2_536608(uint8_t*p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_ble_stack_callback_536620',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,state,present):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  msg=0x20081000;payload=0x20082000;ctx=0x20083000
  m=bytearray([0xa5]*64);m[0x30:0x34]=(ctx if present else 0).to_bytes(4,'little');u.mem_write(msg,bytes(m));u.mem_write(payload,bytes(range(32)))
  u.mem_write(ctx+0x29,bytes([state]));trace=[]
  names=[('copy','audio_ble_stack_copy16_542a44',0x542a44),('state0','audio_ble_stack_state0_5365a6',0x5365a6),('state1','audio_ble_stack_state1_5364a4',0x5364a4),('state2','audio_ble_stack_state2_536608',0x536608)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    if name=='copy':
     dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);trace.append(('copy',dst-msg,src-payload));uc.mem_write(dst,bytes(uc.mem_read(src,16)))
    else:trace.append((name,uc.reg_read(UC_ARM_REG_R0)==msg))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,msg);u.reg_write(UC_ARM_REG_R1,payload);u.reg_write(UC_ARM_REG_R3,0x12345678)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_ble_stack_callback_536620'] if compiled else 0x536620)|1,0x600000,count=2000)
  return bytes(u.mem_read(msg,64)),trace,u.reg_read(UC_ARM_REG_R0)
 cases=0
 for present in (0,1):
  for state in (0,1,2,3,4,255):
   a,b=run(False,state,present),run(True,state,present)
   assert a==b,(state,present,a,b)
   cases+=1
 print('PASS_BLE_STACK_CALLBACK_536620_NATIVE',cases)
