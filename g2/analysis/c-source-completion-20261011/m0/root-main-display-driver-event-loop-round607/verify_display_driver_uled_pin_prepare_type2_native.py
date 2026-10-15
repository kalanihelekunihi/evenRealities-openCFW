#!/usr/bin/env python3
"""Native/C type-2 prepare with real bitmap/status/finalizer/IRQ and controlled bus/delay."""
from itertools import product
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_PRIMASK,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
sources=('display_driver_uled_pin_prepare_type2.c',
         'display_driver_uled_pin_type2_support.c',
         'display_driver_uled_pin_prepare_finalize.c',
         'display_driver_uled_pin_bitmap.c',
         'display_driver_uled_irq_save.c')
stubs='''
#include <stdint.h>
uint32_t display_driver_uled_pin_bus_command_4809c4(uint32_t type,uint8_t*value){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]++;p[1]=type;
p[2]=value?*value:0xffffffffu;return 0;}
void display_driver_uled_delay_4807a0(uint32_t ms){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[3]++;p[4]=ms;
*(volatile uint8_t*)0x20074f56=0;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stubs.c').write_text(stubs);image=d/'type2-prepare.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',*[str(here/x) for x in sources],
                 str(d/'stubs.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_pin_prepare_type2_4c3d9e')
 cases=0
 for pin,gate,queried,status,mode,waiting,old_count,prior in product(
    (0x10,0x34),(0,1),(0,1),(0,1,0x100,0x101),(0,1,2),(0,1),(0,2),(0,1)):
  observed=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   u.mem_map(0x40020000,0x10000)
   for base,data in segments:u.mem_write(base,data)
   for i in range(14):set32(u,0x20073324+i*4,0)
   slot=0x20073324+2*8+(pin>>5)*4
   if queried:set32(u,slot,1<<(pin&31))
   set32(u,0x200001d0,gate)
   u.mem_write(0x200001cc,bytes([mode]))
   set32(u,0x4002012c,status)
   u.mem_write(0x20074f56,bytes([waiting]))
   set32(u,0x20074260,0x20088000 if waiting else 0)
   set32(u,0x20088000,old_count)
   def on_lower(_u,where,size,_user):
    if compiled:return
    if where==0x4809c4:
     set32(u,0x20090000,get32(u,0x20090000)+1)
     set32(u,0x20090004,u.reg_read(UC_ARM_REG_R0))
     ptr=u.reg_read(UC_ARM_REG_R1)
     set32(u,0x20090008,u.mem_read(ptr,1)[0] if ptr else 0xffffffff)
     u.reg_write(UC_ARM_REG_R0,0)
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
    elif where==0x4807a0:
     set32(u,0x2009000c,get32(u,0x2009000c)+1)
     set32(u,0x20090010,u.reg_read(UC_ARM_REG_R0))
     u.mem_write(0x20074f56,b'\x00')
     u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,on_lower,begin=0x4807a0,end=0x4809c4)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_PRIMASK,prior);u.reg_write(UC_ARM_REG_R0,pin)
   u.emu_start((sym if compiled else 0x4c3d9e)|1,0x600000,count=10000)
   cell=get32(u,0x20074260)
   observed.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK),
      bytes(u.mem_read(0x20073324,56)),bytes(u.mem_read(0x20074f56,1)),
      bool(cell),bytes(u.mem_read(0x20090000,20))))
  assert observed[0]==observed[1],(
   pin,gate,queried,status,mode,waiting,old_count,prior,observed)
  cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_PREPARE_TYPE2_NATIVE',cases)
