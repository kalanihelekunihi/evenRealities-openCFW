#!/usr/bin/env python3
"""Compare PMIC transport wrappers and commit through controlled callbacks."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('display_driver_uled_pmic_read_55fc38',0x55fc38),('display_driver_uled_pmic_write_55fc2c',0x55fc2c),('display_driver_uled_pmic_commit_lower_55f9e8',0x55f9e8)]
with tempfile.TemporaryDirectory() as directory:
 image=Path(directory)/'transport.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_pmic_transport.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native in entries:
  for index in (0,1,2):
   for mode in (0,1,2,255):
    observed=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     transport=0x20008000;descriptor=0x20008100;buffer=0x20008200
     u.mem_write(transport,(0x20003001).to_bytes(4,'little')+(0x20003101).to_bytes(4,'little')+(0x20009000).to_bytes(4,'little'))
     u.mem_write(descriptor,transport.to_bytes(4,'little')+bytes([index]))
     u.mem_write(buffer,b'\xa5\xa6\xa7\xa8')
     calls=[]
     def callback(uc,at,size,user):
      r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
      calls.append((at,r0,r1,r3,bytes(uc.mem_read(r2,r3))))
      uc.reg_write(UC_ARM_REG_R0,0x2bad0000)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for at in (0x20003000,0x20003100):u.hook_add(UC_HOOK_CODE,callback,begin=at,end=at)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,descriptor if 'commit' in name else transport)
     u.reg_write(UC_ARM_REG_R1,mode if 'commit' in name else 0x40f)
     u.reg_write(UC_ARM_REG_R2,buffer);u.reg_write(UC_ARM_REG_R3,1)
     u.emu_start((syms[name] if compiled else native)|1,0x600000,count=1000)
     observed.append((u.reg_read(UC_ARM_REG_R0),calls))
    assert observed[0]==observed[1],(name,index,mode,observed)
    cases+=1
 print('PASS_ULED_OPTION_PMIC_TRANSPORT_NATIVE',cases)
