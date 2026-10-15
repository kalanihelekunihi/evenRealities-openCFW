#!/usr/bin/env python3
"""Compare NPMX LDO descriptor calculation to official native body."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'find.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_ldo_find.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for base in (0,0x20070f78,0xfffffff0):
  for index in (0,1,2,255,256,0xffffffff):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob);u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for at,data in segments:u.mem_write(at,data)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,base);u.reg_write(UC_ARM_REG_R1,index)
    u.emu_start((syms['display_driver_uled_pmic_ldo_find_55face'] if compiled else 0x55face)|1,0x600000,count=50)
    observed.append(u.reg_read(UC_ARM_REG_R0))
   assert observed[0]==observed[1],(base,index,observed)
   cases+=1
 print('PASS_ULED_OPTION_LDO_FIND_NATIVE',cases)
