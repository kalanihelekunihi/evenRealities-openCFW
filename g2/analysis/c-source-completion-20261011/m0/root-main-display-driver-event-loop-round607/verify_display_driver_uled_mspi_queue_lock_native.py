#!/usr/bin/env python3
"""Native/C queue snapshot-lock arithmetic at Apollo 0x538d18."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stub='''
#include <stdint.h>
uint32_t display_driver_uled_irq_save_473940(void){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]++;
return *(volatile uint32_t*)0x20090100;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'lock.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_dma_queue_lock.c'),
                 str(d/'stub.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_dma_queue_lock_538d18')
 cases=0
 for count in (0,1,0xff,0x100,0x101,0x200,0xffffff00):
  for producer in (0,1,0x7f,0x80,0xfe,0xff,0x100,0xffffffff):
   for mask in (0,1):
    observed=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     q=0x20080000;set32(u,q+0x20,count);set32(u,q+0x24,0x20082000)
     set32(u,0x20082004,0x20083000)
     set32(u,0x20082008,0x20083004)
     set32(u,0x20083000,0x12345678)
     set32(u,0x20083004,producer)
     set32(u,0x20090100,mask)
     def on_irq_save(_u,where,size,_user):
      if compiled or where!=0x473940:return
      set32(u,0x20090000,get32(u,0x20090000)+1)
      u.reg_write(UC_ARM_REG_R0,get32(u,0x20090100))
      u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,on_irq_save,begin=0x473940,end=0x473940)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,q)
     u.emu_start((sym if compiled else 0x538d18)|1,0x600000,count=1000)
     observed.append((u.reg_read(UC_ARM_REG_R0),
       bytes(u.mem_read(q,40)),bytes(u.mem_read(0x20090000,4))))
    assert observed[0]==observed[1],(count,producer,mask,observed)
    cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_QUEUE_LOCK_NATIVE',cases)
