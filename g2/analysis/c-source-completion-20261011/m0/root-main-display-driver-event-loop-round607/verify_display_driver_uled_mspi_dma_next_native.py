#!/usr/bin/env python3
"""Native/C MMIO and return oracle for Apollo DMA-next provider 0x4bfdf4."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stub='''
#include <stdint.h>
uint32_t display_driver_uled_mspi_dma_pin_prepare_4c44bc(uint32_t a,uint32_t b){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]=a;p[1]=b;p[2]++;
return *(volatile uint32_t*)0x20090100;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'next.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_dma_next.c'),
                 str(d/'stub.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_dma_next_4bfdf4')
 cases=0
 for instance in (0,1,3):
  for ring_size in (1,2,4,17):
   for cursor in (0,1,3,0xfffffffe):
    for pin_result in (0,3):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      u.mem_map(0x40060000,0x10000)
      for base,data in segments:u.mem_write(base,data)
      h=0x20080000;set32(u,h+4,instance)
      set32(u,h+0x848,ring_size);set32(u,h+0x850,cursor)
      set32(u,h+0x854,0x20082000)
      for i in range(17):
       for j in range(4):set32(u,0x20082000+i*0x18+j*4,0xa5000000+i*16+j)
      base=0x40060000+(instance<<12)
      for offset in (0x100,0x108,0x10c,0x110):set32(u,base+offset,0xfeed0000+offset)
      set32(u,0x20090100,pin_result)
      writes=[]
      def on_write(_u,access,address,size,value,_user):
       if access==UC_HOOK_MEM_WRITE and 0x40060000<=address<0x40070000:
        writes.append((address,size,value))
      u.hook_add(UC_HOOK_MEM_WRITE,on_write)
      def on_pin(_u,where,size,_user):
       if compiled or where!=0x4c44bc:return
       set32(u,0x20090000,u.reg_read(UC_ARM_REG_R0))
       set32(u,0x20090004,u.reg_read(UC_ARM_REG_R1))
       set32(u,0x20090008,get32(u,0x20090008)+1)
       u.reg_write(UC_ARM_REG_R0,get32(u,0x20090100))
       u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
      u.hook_add(UC_HOOK_CODE,on_pin,begin=0x4c44bc,end=0x4c44bc)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_R0,h)
      u.emu_start((sym if compiled else 0x4bfdf4)|1,0x600000,count=2000)
      observed.append((u.reg_read(UC_ARM_REG_R0),
        bytes(u.mem_read(0x20090000,12)),
        bytes(u.mem_read(base+0x100,0x14)),writes))
     assert observed[0]==observed[1],(instance,ring_size,cursor,pin_result,observed)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_DMA_NEXT_NATIVE',cases)
