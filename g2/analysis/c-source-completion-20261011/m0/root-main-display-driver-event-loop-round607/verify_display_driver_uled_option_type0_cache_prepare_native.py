#!/usr/bin/env python3
"""Compare cache preparation writes for bounded range and full-cache inputs."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'cache.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_cache_prepare.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 for active in (False,True):
  for geometry in (0,(1<<13)|(2<<3)):
   cases.append((active,geometry,None))
   for address,length in ((0x20003000,0),(0x20003001,1),(0x2000301f,1),(0x20003020,32),(0x20003003,33),(0x20003000,0xffffffff)):
    cases.append((active,geometry,(address,length)))
 for active,geometry,range_ in cases:
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000);u.mem_map(0xe000e000,0x2000)
   for base,data in segments:u.mem_write(base,data)
   u.mem_write(0xe000ed14,(0x10000 if active else 0).to_bytes(4,'little'))
   u.mem_write(0xe000ed80,geometry.to_bytes(4,'little'))
   if range_:
    u.mem_write(0x20001000,range_[0].to_bytes(4,'little')+range_[1].to_bytes(4,'little'))
   writes=[]
   def memory(uc,access,address,size,value,user):
    if 0xe000e000<=address<0xe0010000:writes.append((address,size,value))
   u.hook_add(UC_HOOK_MEM_WRITE,memory)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20001000 if range_ else 0)
   u.emu_start((syms['display_driver_uled_prepare_transfer_47510e'] if compiled else 0x47510e)|1,0x600000,count=1000)
   observations.append((u.reg_read(UC_ARM_REG_R0),writes))
  assert observations[0]==observations[1],(active,geometry,range_,observations)
 print('PASS_ULED_OPTION_TYPE0_CACHE_PREPARE_NATIVE',len(cases))
