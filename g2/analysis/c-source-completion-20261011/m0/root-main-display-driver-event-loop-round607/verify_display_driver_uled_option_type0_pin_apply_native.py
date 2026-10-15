#!/usr/bin/env python3
"""Compare pin capability gating, register writes, and IRQ state."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP,UC_ARM_REG_PRIMASK
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'pin.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_pin_apply.c'),str(here/'display_driver_uled_irq_save.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for pin in range(228):
  for configuration in (0,0x400,0x800,0xc00,0x2000,0xc000,0xe000,0xffffffff):
   for mask in (0,1):
    observations=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40010000,0x1000)
     for base,data in segments:u.mem_write(base,data)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,pin);u.reg_write(UC_ARM_REG_R1,configuration);u.reg_write(UC_ARM_REG_PRIMASK,mask)
     u.emu_start((syms['display_driver_uled_pin_apply_480f0c'] if compiled else 0x480f0c)|1,0x600000,count=500)
     register=0x40010000+pin*4 if pin<224 else 0x40010000
     observations.append((u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_PRIMASK),bytes(u.mem_read(register,4)),bytes(u.mem_read(0x40010400,4))))
    assert observations[0]==observations[1],(pin,configuration,mask,observations)
    cases+=1
 print('PASS_ULED_OPTION_TYPE0_PIN_APPLY_NATIVE',cases)
