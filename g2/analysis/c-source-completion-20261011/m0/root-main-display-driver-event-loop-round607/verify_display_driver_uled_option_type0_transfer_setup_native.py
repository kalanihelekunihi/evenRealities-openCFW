#!/usr/bin/env python3
"""Compare DMA transfer setup validation and state/MMIO writes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'setup.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_transfer_setup.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[]
 for channel in range(14):
  for count,base,busy in ((2,0x20003000,0),(1,0x20003000,0),(2,0,0),(2,0x20003000,1)):
   cases.append((channel,count,base,busy,False,False))
 cases += [(0,2,0x20003000,0,True,False),(0,2,0x20003000,0,False,True),(0x100,3,0x20003000,0,False,False)]
 for channel,count,base,busy,null_param,null_out in cases:
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40050000,0x20000)
   for address,data in segments:u.mem_write(address,data)
   index=channel&255
   state=0x2006ef28+(index if index<12 else 0)*44
   u.mem_write(state,(0x01000000 if busy else 0).to_bytes(4,'little'))
   args=count.to_bytes(4,'little')+base.to_bytes(4,'little')+bytes((1,0,0,0))
   u.mem_write(0x20002000,args)
   u.mem_write(0x20001000,(0xdeadbeef).to_bytes(4,'little'))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,channel)
   u.reg_write(UC_ARM_REG_R1,0 if null_param else 0x20002000)
   u.reg_write(UC_ARM_REG_R2,0 if null_out else 0x20001000)
   u.emu_start((syms['display_driver_uled_setup_lower_538d58'] if compiled else 0x538d58)|1,0x600000,count=3000)
   observations.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20001000,4)),bytes(u.mem_read(state,44)),bytes(u.mem_read(0x40050000,0x14000))))
  assert observations[0]==observations[1],(channel,count,base,busy,null_param,null_out,observations[0][:3],observations[1][:3])
 print('PASS_ULED_OPTION_TYPE0_TRANSFER_SETUP_NATIVE',len(cases))
