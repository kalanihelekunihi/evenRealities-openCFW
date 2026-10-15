#!/usr/bin/env python3
"""Compare Hongshi register-read native/C descriptor and return."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('unsigned display_driver_uled_type0_packet_59cc40(void *p){return 0;}\n')
 image=Path(directory)/'register.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_type1_read_register.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for bank in (0,6,255,0x1234):
  for mode in (0,1,2,255):
   for count in (0,1,4):
    observations=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     u.mem_write(0x20074510,(0x12345678).to_bytes(4,'little'))
     def copy(uc,at,size,user):
      dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2)
      uc.mem_write(dst,bytes(uc.mem_read(src,n)));uc.reg_write(UC_ARM_REG_R0,dst);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     if not compiled:u.hook_add(UC_HOOK_CODE,copy,begin=0x439c04,end=0x439c04)
     calls=[]
     def packet(uc,at,size,user):
      calls.append(bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R0),28)))
      uc.reg_write(UC_ARM_REG_R0,0x44);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     target=syms['display_driver_uled_type0_packet_59cc40']&~1 if compiled else 0x59cc40
     u.hook_add(UC_HOOK_CODE,packet,begin=target,end=target)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,bank);u.reg_write(UC_ARM_REG_R1,0x20001000);u.reg_write(UC_ARM_REG_R2,count);u.reg_write(UC_ARM_REG_R3,mode)
     u.emu_start((syms['display_driver_uled_type1_read_register_5bbe3e'] if compiled else 0x5bbe3e)|1,0x600000,count=1000)
     observations.append((calls,u.reg_read(UC_ARM_REG_R0)))
    assert observations[0]==observations[1],(bank,mode,count,observations)
    cases+=1
 print('PASS_ULED_TYPE1_READ_REGISTER_NATIVE',cases)
