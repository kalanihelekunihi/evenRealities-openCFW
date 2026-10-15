#!/usr/bin/env python3
"""Compare full flash-bus pin dispatch to native over every option byte class."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;u32 g2_codec_pin_function(u32 a,u32 b){return 0;}')
 image=Path(directory)/'bus.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_flash_bus_prepare.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in (0,1,2,3,4,255):
  for choice in (*range(20),255,256,0xffffffff):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    calls=[]
    def lower(uc,at,size,user):
     pin=uc.reg_read(UC_ARM_REG_R0);cfg=uc.reg_read(UC_ARM_REG_R1)
     calls.append((pin,cfg));uc.reg_write(UC_ARM_REG_R0,(pin^cfg)&0xffffffff)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    target=syms['g2_codec_pin_function']&~1 if compiled else 0x480f0c
    u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,mode);u.reg_write(UC_ARM_REG_R1,choice)
    u.emu_start((syms['display_driver_uled_flash_bus_prepare_4c3500'] if compiled else 0x4c3500)|1,0x600000,count=3000)
    observed.append((u.reg_read(UC_ARM_REG_R0),calls))
   assert observed[0]==observed[1],(mode,choice,observed)
   cases+=1
 print('PASS_ULED_FLASH_BUS_PREPARE_NATIVE',cases)
