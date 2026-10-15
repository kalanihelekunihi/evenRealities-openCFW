#!/usr/bin/env python3
"""Native/C type-4 pin chain with real bitmap, power, finalize and IRQ bodies."""
from itertools import product
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
sources=('display_driver_uled_pin_prepare_type4.c',
         'display_driver_uled_pin_prepare_finalize.c',
         'display_driver_uled_pin_bitmap.c',
         'display_driver_uled_power_control.c',
         'display_driver_uled_irq_save.c')
stub='''
#include <stdint.h>
void display_driver_uled_delay_4807a0(uint32_t ms){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]++;p[1]=ms;
*(volatile uint8_t*)0x20074f57=0;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'real-chain.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',*[str(here/x) for x in sources],
                 str(d/'stub.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_pin_prepare_type4_4c3f2a')
 cases=0
 for pin,queried,other_bit,flag,disabled,enabled,flag59,prior in product(
    (0x10,0x30),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1),(0,1)):
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   u.mem_map(0x40000000,0x10000)
   for base,data in segments:u.mem_write(base,data)
   for i in range(14):set32(u,0x20073324+i*4,0)
   slot=0x20073324+4*8+(pin>>5)*4
   set32(u,slot,(1<<(pin&31)) if queried else 0)
   if other_bit:set32(u,0x20073324+4*8,get32(u,0x20073324+4*8)|1)
   u.mem_write(0x20074f57,bytes([flag]))
   u.mem_write(0x20074f59,bytes([flag59]))
   u.mem_write(0x20004536,bytes([disabled]))
   set32(u,0x20074250,enabled)
   set32(u,0x20073f30,0x12345678)
   set32(u,0x20074264,0x20088000 if flag else 0)
   set32(u,0x20088000,2)
   set32(u,0x40004020,0xabcdef00)
   set32(u,0x40004044,0x12345679)
   def on_delay(_u,where,size,_user):
    if compiled or where!=0x4807a0:return
    n=get32(u,0x20090000)+1;set32(u,0x20090000,n)
    set32(u,0x20090004,u.reg_read(UC_ARM_REG_R0))
    u.mem_write(0x20074f57,b'\x00')
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,on_delay,begin=0x4807a0,end=0x4807a0)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_PRIMASK,prior);u.reg_write(UC_ARM_REG_R0,pin)
   u.emu_start((sym if compiled else 0x4c3f2a)|1,0x600000,count=20000)
   cell=get32(u,0x20074264)
   observations.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK),
      bytes(u.mem_read(0x20073324,56)),
      bytes(u.mem_read(0x20074f57,3)),bool(cell),
      bytes(u.mem_read(0x40004020,4)),bytes(u.mem_read(0x40004044,4)),
      bytes(u.mem_read(0x20090000,8))))
  assert observations[0]==observations[1],(
    pin,queried,other_bit,flag,disabled,enabled,flag59,prior,observations)
  cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_PREPARE_TYPE4_REAL_CHAIN_NATIVE',cases)
