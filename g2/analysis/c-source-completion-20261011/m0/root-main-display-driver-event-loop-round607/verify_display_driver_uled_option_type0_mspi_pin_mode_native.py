#!/usr/bin/env python3
"""Compare complete group/mode grid of native MSPI pin calls."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('void display_driver_uled_pin_apply_480f0c(unsigned a,unsigned b){(void)a;(void)b;}\n')
 image=Path(directory)/'pins.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_mspi_pin_mode.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for group in range(4):
  for mode in range(256):
   observations=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    for address in range(0x20000138,0x200001b0,4):
     u.mem_write(address,(address^0x12345678).to_bytes(4,'little'))
    calls=[]
    def lower(uc,at,size,user):
     calls.append((uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    target=(syms['display_driver_uled_pin_apply_480f0c']&~1) if compiled else 0x480f0c
    u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,group);u.reg_write(UC_ARM_REG_R1,mode)
    u.emu_start((syms['display_driver_uled_mspi_pin_mode_4c32b4'] if compiled else 0x4c32b4)|1,0x600000,count=3000)
    observations.append(calls)
   assert observations[0]==observations[1],(group,mode,observations)
   cases+=1
 print('PASS_ULED_OPTION_TYPE0_MSPI_PIN_MODE_NATIVE',cases)
