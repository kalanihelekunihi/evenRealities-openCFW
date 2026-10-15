#!/usr/bin/env python3
"""Native/C MMIO oracle for Apollo type-2 bus status 0x480c56."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_READ
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stub='''
#include <stdint.h>
void display_driver_uled_pin_prepare_wait_4c387e(volatile uint8_t*a,uint32_t*b){(void)a;(void)b;}
uint32_t display_driver_uled_irq_save_473940(void){return 0;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'status.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_pin_type2_support.c'),
                 str(d/'stub.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_pin_bus_status_480c56')
 cases=0
 for status in (0,1,2,0x100,0x101,0x102,0xffffffff):
  observed=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
   u.mem_map(0x40020000,0x10000)
   for base,data in segments:u.mem_write(base,data)
   set32(u,0x4002012c,status);u.mem_write(0x20088000,b'\xcc')
   reads=[]
   def on_read(_u,kind,where,size,value,_user):
    if where==0x4002012c:reads.append((where,size))
   u.hook_add(UC_HOOK_MEM_READ,on_read)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20088000)
   u.emu_start((sym if compiled else 0x480c56)|1,0x600000,count=1000)
   observed.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20088000,1)),reads))
  assert observed[0]==observed[1],(status,observed)
  cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_PIN_TYPE2_STATUS_NATIVE',cases)
