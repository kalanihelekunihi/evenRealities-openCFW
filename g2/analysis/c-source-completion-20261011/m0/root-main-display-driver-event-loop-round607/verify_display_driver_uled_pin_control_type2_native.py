#!/usr/bin/env python3
"""Native/C type-2 pin control with real bitmap/IRQ and controlled bus command."""
from itertools import product
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stub='''
#include <stdint.h>
uint32_t display_driver_uled_pin_bus_command_4809c4(uint32_t kind,uint8_t *value){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]++;p[1]=kind;p[2]=*value;
return 0;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'type2-control.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',
                 str(here/'display_driver_uled_pin_control_type2.c'),
                 str(here/'display_driver_uled_pin_bitmap.c'),
                 str(here/'display_driver_uled_irq_save.c'),
                 str(d/'stub.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_pin_control_type2_4c3e9a')
 cases=0
 for pin,enabled,other_bit,prior,flag in product(
    (0x10,0x30),(0,1),(0,1),(0,1),(0,1)):
  observed=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   for base,data in segments:u.mem_write(base,data)
   for i in range(14):set32(u,0x20073324+i*4,0)
   slot=0x20073324+2*8+(pin>>5)*4
   if enabled:set32(u,slot,1<<(pin&31))
   if other_bit:set32(u,0x20073324+2*8,1)
   u.mem_write(0x20074f56,bytes([flag]))
   set32(u,0x20074260,0x20088000)
   def on_bus(_u,where,size,_user):
    if compiled or where!=0x4809c4:return
    n=int.from_bytes(u.mem_read(0x20090000,4),'little')+1
    set32(u,0x20090000,n)
    set32(u,0x20090004,u.reg_read(UC_ARM_REG_R0))
    value=u.mem_read(u.reg_read(UC_ARM_REG_R1),1)[0]
    set32(u,0x20090008,value)
    u.reg_write(UC_ARM_REG_R0,0)
    u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,on_bus,begin=0x4809c4,end=0x4809c4)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_PRIMASK,prior);u.reg_write(UC_ARM_REG_R0,pin)
   u.emu_start((sym if compiled else 0x4c3e9a)|1,0x600000,count=4000)
   observed.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK),
     bytes(u.mem_read(0x20073324,56)),bytes(u.mem_read(0x20074f56,1)),
     bytes(u.mem_read(0x20074260,4)),bytes(u.mem_read(0x20090000,12))))
  assert observed[0]==observed[1],(pin,enabled,other_bit,prior,flag,observed)
  cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_CONTROL_TYPE2_NATIVE',cases)
