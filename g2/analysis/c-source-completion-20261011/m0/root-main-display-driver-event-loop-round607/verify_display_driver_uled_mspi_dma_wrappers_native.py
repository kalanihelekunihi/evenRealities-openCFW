#!/usr/bin/env python3
"""Compare 0x4bfd44/0x4bfd62 with native instructions under controlled callees."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stubs='''
#include <stdint.h>
static uint32_t call(uint32_t id,uint32_t a,uint32_t b){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;uint32_t n=p[0];
p[1+n*3]=id;p[2+n*3]=a;p[3+n*3]=b;p[0]=n+1;
return *(volatile uint32_t*)(0x20090100+id*4);}
uint32_t display_driver_uled_mspi_dma_pin_prepare_4c44bc(uint32_t a,uint32_t b){return call(1,a,b);}
uint32_t display_driver_uled_mspi_dma_queue_start_538e3c(uint32_t a){return call(2,a,0);}
uint32_t display_driver_uled_mspi_dma_queue_stop_538e8c(uint32_t a){return call(3,a,0);}
'''
targets={0x4c44bc:1,0x538e3c:2,0x538e8c:3}
entries=[('display_driver_uled_mspi_dma_start_4bfd44',0x4bfd44),
         ('display_driver_uled_mspi_dma_stop_4bfd62',0x4bfd62)]
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stubs.c').write_text(stubs);image=d/'wrappers.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_dma_wrappers.c'),
                 str(d/'stubs.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address in entries:
  for instance in (0,1,3,0xf0):
   for pin_status in (0,3):
    for queue_status in (0,5):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      for base,data in segments:u.mem_write(base,data)
      h=0x20080000;set32(u,h+4,instance);set32(u,h+0x828,0x20071234)
      set32(u,0x20090104,pin_status)
      set32(u,0x20090108,queue_status)
      set32(u,0x2009010c,queue_status)
      def on_call(_u,where,size,_user):
       if compiled or where not in targets:return
       id=targets[where];a=u.reg_read(UC_ARM_REG_R0)
       b=u.reg_read(UC_ARM_REG_R1) if id==1 else 0
       n=get32(u,0x20090000)
       for i,v in enumerate((id,a,b)):set32(u,0x20090004+(n*3+i)*4,v)
       set32(u,0x20090000,n+1)
       u.reg_write(UC_ARM_REG_R0,get32(u,0x20090100+id*4))
       u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
      u.hook_add(UC_HOOK_CODE,on_call,begin=min(targets),end=max(targets))
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_R0,h)
      u.emu_start((syms[name] if compiled else address)|1,0x600000,count=1000)
      observed.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20090000,64))))
     assert observed[0]==observed[1],(name,instance,pin_status,queue_status,observed)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_DMA_WRAPPERS_NATIVE',cases)
