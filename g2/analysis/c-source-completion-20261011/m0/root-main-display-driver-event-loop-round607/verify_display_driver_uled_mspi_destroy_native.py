#!/usr/bin/env python3
"""Bounded native/C oracle for Apollo MSPI destroy 0x4c240e.

These cases deliberately avoid the six unresolved direct callees and queue
callbacks. They validate only the reached branches, not the whole function.
"""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP

here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
stubs='''
#include <stdint.h>
uint32_t display_driver_uled_mspi_queue_snapshot_53901a(uint32_t a,uint32_t*b){(void)a;(void)b;return 0;}
uint32_t display_driver_uled_mspi_queue_release_5390fc(uint32_t a){(void)a;return 0;}
uint32_t display_driver_uled_mspi_dma_start_4bfd44(uint32_t*a){(void)a;return 0;}
uint32_t display_driver_uled_mspi_dma_stop_4bfd62(uint32_t*a){(void)a;return 0;}
uint32_t display_driver_uled_mspi_dma_next_4bfdf4(uint32_t*a){(void)a;return 0;}
uint32_t display_driver_uled_mspi_pin_control_4c4530(uint32_t a,uint32_t b){(void)a;(void)b;return 0;}
'''
def set32(u,a,v):u.mem_write(a,(v&0xffffffff).to_bytes(4,'little'))
def get32(u,a):return int.from_bytes(u.mem_read(a,4),'little')
with tempfile.TemporaryDirectory() as directory:
 d=Path(directory);(d/'stubs.c').write_text(stubs);image=d/'destroy.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(here/'display_driver_uled_mspi_destroy.c'),
                 str(d/'stubs.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  sym=next(s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()
           if s.name=='display_driver_uled_mspi_child_4c240e')
 cases=0
 for kind in ('null','bad','idle','queued_no_owner','active_clean','active_fatal'):
  for instance in (0,1,3):
   for flags in (0,0x40,0x1880):
    if kind=='active_clean' and flags==0:continue
    if kind=='active_fatal' and flags!=0x1880:continue
    observed=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     u.mem_map(0x40060000,0x10000)
     for base,data in segments:u.mem_write(base,data)
     h=0 if kind=='null' else 0x20080000
     set32(u,0x20080000,0x01bebebe if kind!='bad' else 0xdeadbeef)
     set32(u,0x20080004,instance)
     u.mem_write(0x20080000+0x8c9,b'\x04')
     if kind in ('queued_no_owner','active_clean','active_fatal'):
      set32(u,0x20080020,1)
     if kind in ('active_clean','active_fatal'):
      u.mem_write(0x20080000+0x83c,b'\x01')
      set32(u,0x20080000+0x840,1)
      set32(u,0x20080000+0x848,4)
      set32(u,0x20080000+0x850,0)
      set32(u,0x20080000+0x854,0x20082000)
     base=0x40060000+(instance<<12)
     set32(u,base+0x100,0xfeed4321)
     set32(u,base+0x104,0)
     set32(u,base+0x200,0xabcdef7f)
     set32(u,base+0x204,0)
     set32(u,base+0x30,0x12345678)
     writes=[]
     def record(_u,access,address,size,value,_user):
      if access==UC_HOOK_MEM_WRITE and 0x40060000<=address<0x40070000:
       writes.append((address,size,value))
     u.hook_add(UC_HOOK_MEM_WRITE,record)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,h);u.reg_write(UC_ARM_REG_R1,flags)
     u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,0)
     u.emu_start((sym if compiled else 0x4c240e)|1,0x600000,count=20000)
     observed.append((u.reg_read(UC_ARM_REG_R0),
       bytes(u.mem_read(0x20080000,0x8d0)),
       bytes(u.mem_read(base,0x2b8)),writes))
    assert observed[0]==observed[1],(kind,instance,hex(flags),
      observed[0][0],observed[1][0],observed[0][3],observed[1][3])
    cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_DESTROY_BOUNDED_NATIVE',cases)
