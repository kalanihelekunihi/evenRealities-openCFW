#!/usr/bin/env python3
"""Native/C side-effect oracle for Apollo prepare wait/finalize pair."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stub='''
#include <stdint.h>
void display_driver_uled_delay_4807a0(uint32_t ms){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]++;p[1]=ms;
uint32_t limit=*(volatile uint32_t*)0x20090100;
if(limit && p[0]>=limit)*(volatile uint8_t*)0x20074f57=0;}
'''
entries=[('display_driver_uled_pin_prepare_wait_4c387e',0x4c387e),
         ('display_driver_uled_pin_prepare_finalize_4c3ef4',0x4c3ef4)]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'finalize.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_pin_prepare_finalize.c'),
                 str(here/'display_driver_uled_irq_save.c'),str(d/'stub.c'),
                 '-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address in entries:
  for flag in (0,1):
   for remaining in (0,1,2,3,4):
    for clear_after in (0,1,2,3):
     for prior in (0,1):
      observed=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
       u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
       for base,data in segments:u.mem_write(base,data)
       u.mem_write(0x20074f57,bytes([flag]));u.mem_write(0x20074f59,b'\x00')
       set32(u,0x20074264,0x20088000)
       set32(u,0x20088000,remaining);set32(u,0x20090100,clear_after)
       def on_delay(_u,where,size,_user):
        if compiled or where!=0x4807a0:return
        n=get32(u,0x20090000)+1;set32(u,0x20090000,n)
        set32(u,0x20090004,u.reg_read(UC_ARM_REG_R0))
        if clear_after and n>=clear_after:u.mem_write(0x20074f57,b'\x00')
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
       u.hook_add(UC_HOOK_CODE,on_delay,begin=0x4807a0,end=0x4807a0)
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
       u.reg_write(UC_ARM_REG_PRIMASK,prior)
       u.reg_write(UC_ARM_REG_R0,0x20074f57 if address==0x4c387e else 0x20088000)
       u.reg_write(UC_ARM_REG_R1,0x20088000)
       u.emu_start((syms[name] if compiled else address)|1,0x600000,count=10000)
       observed.append((u.reg_read(UC_ARM_REG_PRIMASK),
         bytes(u.mem_read(0x20074f57,3)),
         bytes(u.mem_read(0x20074264,4)),
         bytes(u.mem_read(0x20088000,4)),
         bytes(u.mem_read(0x20090000,8))))
      assert observed[0]==observed[1],(name,flag,remaining,clear_after,prior,observed)
      cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_PREPARE_FINALIZE_NATIVE',cases)
