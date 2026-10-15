#!/usr/bin/env python3
"""Native/C queue snapshot 0x53901a under a controlled lower lock call."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_PC,UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stub='''
#include <stdint.h>
uint32_t display_driver_uled_mspi_dma_queue_lock_538d18(uint32_t*q){
volatile uint32_t*p=(volatile uint32_t*)0x20090000;p[0]++;p[1]=(uint32_t)q;return 0;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stub.c').write_text(stub);image=d/'snapshot.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_dma_queue_snapshot_release.c'),
                 str(d/'stub.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_queue_snapshot_53901a')
 cases=0
 for kind in ('null','bad','valid'):
  for out_kind in ('null','valid'):
   for queue_count in (0,1,8):
    for pending in (False,True):
     for status in (0,1,0x40,0x1880,0xffffffff):
      observations=[]
      for compiled in (False,True):
       u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
       u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
       u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
       u.mem_map(0x40060000,0x10000)
       for base,data in segments:u.mem_write(base,data)
       q=0 if kind=='null' else 0x20080000
       out=0 if out_kind=='null' else 0x20083000
       set32(u,0x20080000,0x01cdcdcd if kind=='valid' else 0xdeadbeef)
       set32(u,0x20080010,0x20 if pending else 0x10)
       set32(u,0x20080014,0x10)
       set32(u,0x2008001c,7)
       set32(u,0x20080020,queue_count)
       set32(u,0x20080024,0x20082000)
       set32(u,0x20082018,0x40060200)
       set32(u,0x2008201c,0x1880)
       set32(u,0x20082020,0x40)
       set32(u,0x20082024,1)
       set32(u,0x40060200,status)
       u.mem_write(0x20083000,b'\xcc'*16)
       def on_lock(_u,where,size,_user):
        if compiled or where!=0x538d18:return
        n=int.from_bytes(u.mem_read(0x20090000,4),'little')
        set32(u,0x20090000,n+1)
        set32(u,0x20090004,u.reg_read(UC_ARM_REG_R0))
        u.reg_write(UC_ARM_REG_R0,0)
        u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
       u.hook_add(UC_HOOK_CODE,on_lock,begin=0x538d18,end=0x538d18)
       u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
       u.reg_write(UC_ARM_REG_R0,q);u.reg_write(UC_ARM_REG_R1,out)
       u.emu_start((sym if compiled else 0x53901a)|1,0x600000,count=2000)
       observations.append((u.reg_read(UC_ARM_REG_R0),
          bytes(u.mem_read(0x20083000,16)),bytes(u.mem_read(0x20090000,8))))
      assert observations[0]==observations[1],(kind,out_kind,queue_count,pending,status,observations)
      cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_QUEUE_SNAPSHOT_NATIVE',cases)
