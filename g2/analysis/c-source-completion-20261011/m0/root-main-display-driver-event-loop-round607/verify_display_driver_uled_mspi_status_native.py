#!/usr/bin/env python3
"""Compare MSPI status read/clear MMIO contracts with native instructions."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import (Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,
                     UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE)
from unicorn.arm_const import (UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,
                               UC_ARM_REG_R2,UC_ARM_REG_SP)
source=Path(__file__).with_name('display_driver_uled_mspi_status.c')
blob=(Path(__file__).resolve().parents[4]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('display_driver_uled_mspi_child_4c2392',0x4c2392),
         ('display_driver_uled_mspi_child_4c23de',0x4c23de)]
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'mspi.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
                 '-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000',str(source),'-o',str(image)],
                check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file)
  segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,address in entries:
  for handle_kind in ('null','bad','good'):
   for instance in (0,1,3):
    for argument in (0,1,0x100,0x12345678,0xffffffff):
     observations=[]
     for compiled in (False,True):
      cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
      cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
      cpu.mem_map(0x40060000,0x10000)
      for base,data in segments:cpu.mem_write(base,data)
      handle=0 if handle_kind=='null' else 0x20080000
      magic=0x01bebebe if handle_kind=='good' else 0xdeadbeef
      cpu.mem_write(0x20080000,magic.to_bytes(4,'little')+
                    instance.to_bytes(4,'little'))
      base=0x40060000+(instance<<12)
      cpu.mem_write(base+0x200,(0x0f0ff00f).to_bytes(4,'little'))
      cpu.mem_write(base+0x204,(0xa5a5ff00).to_bytes(4,'little'))
      output=0x20081000;cpu.mem_write(output,(0xcccccccc).to_bytes(4,'little'))
      cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
      cpu.reg_write(UC_ARM_REG_R0,handle)
      cpu.reg_write(UC_ARM_REG_R1,output if address==0x4c2392 else argument)
      cpu.reg_write(UC_ARM_REG_R2,argument)
      accesses=[]
      def access(u,kind,where,size,value,_user):
       if 0x40060000<=where<0x40070000:
        accesses.append((kind,where-0x40060000,size,value if kind==2 else None))
      cpu.hook_add(UC_HOOK_MEM_READ|UC_HOOK_MEM_WRITE,access)
      cpu.emu_start((syms[name] if compiled else address)|1,0x600000,count=100)
      observations.append((cpu.reg_read(UC_ARM_REG_R0),
                           int.from_bytes(cpu.mem_read(output,4),'little'),
                           int.from_bytes(cpu.mem_read(base+0x208,4),'little'),
                           accesses))
     assert observations[0]==observations[1],(
      name,handle_kind,instance,hex(argument),observations)
     cases+=1
 print('PASS_DISPLAY_DRIVER_ULED_MSPI_STATUS_NATIVE',cases)
