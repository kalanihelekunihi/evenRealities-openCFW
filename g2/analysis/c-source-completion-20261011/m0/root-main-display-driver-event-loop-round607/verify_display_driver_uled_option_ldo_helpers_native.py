#!/usr/bin/env python3
"""Compare LDO helper transport calls and byte updates to native code."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
entries=[('display_driver_uled_pmic_ldo_commit_lower_55faa8',0x55faa8),('display_driver_uled_pmic_ldo_commit_55fad8',0x55fad8),('display_driver_uled_pmic_ldo_switch_55fb7c',0x55fb7c),('display_driver_uled_pmic_ldo_config_55fae2',0x55fae2)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('typedef unsigned u32;u32 display_driver_uled_pmic_read_55fc38(u32 a,u32 b,void*c,u32 d){return 0;}u32 display_driver_uled_pmic_write_55fc2c(u32 a,u32 b,const void*c,u32 d){return 0;}')
 image=Path(directory)/'ldo.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_ldo_helpers.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native in entries:
  for index in (0,1,2):
   for value in (0,1,255):
    for status in (0,0x2bad0000):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      for base,data in segments:u.mem_write(base,data)
      descriptor=0x20070fc8;config=0x20008800
      u.mem_write(descriptor,(0x20009000).to_bytes(4,'little')+bytes([index]))
      u.mem_write(config,bytes([value,0,0,0,5,0,0,0]))
      calls=[]
      def lower(uc,at,size,user):
       r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
       if at==(syms['display_driver_uled_pmic_read_55fc38']&~1 if compiled else 0x55fc38):
        calls.append(('read',r0,r1,r3));uc.mem_write(r2,b'\xa5');uc.reg_write(UC_ARM_REG_R0,status)
       else:
        calls.append(('write',r0,r1,r3,bytes(uc.mem_read(r2,r3))));uc.reg_write(UC_ARM_REG_R0,0x2bad0000)
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      for n,at in [('display_driver_uled_pmic_read_55fc38',0x55fc38),('display_driver_uled_pmic_write_55fc2c',0x55fc2c)]:
       target=syms[n]&~1 if compiled else at
       u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_R0,descriptor);u.reg_write(UC_ARM_REG_R1,config if 'config' in name else value)
      u.emu_start((syms[name] if compiled else native)|1,0x600000,count=2000)
      observed.append((u.reg_read(UC_ARM_REG_R0),calls))
     assert observed[0]==observed[1],(name,index,value,status,observed)
     cases+=1
 print('PASS_ULED_OPTION_LDO_HELPERS_NATIVE',cases)
