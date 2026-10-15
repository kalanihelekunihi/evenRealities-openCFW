#!/usr/bin/env python3
"""Compare four PMIC helpers to official Apollo with transport callees bounded."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_pmic_read_55fc38',0x55fc38),('display_driver_uled_pmic_write_55fc2c',0x55fc2c),('display_driver_uled_pmic_commit_lower_55f9e8',0x55f9e8)]
entries=[('display_driver_uled_pmic_find_55fa0e',0x55fa0e),('display_driver_uled_pmic_enable_55fa40',0x55fa40),('display_driver_uled_pmic_voltage_55fa22',0x55fa22),('display_driver_uled_pmic_commit_55fa18',0x55fa18)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d){{return 0;}}' for name,at in callees))
 image=Path(directory)/'pmic.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_pmic_helpers.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native in entries:
  for index in (0,1,2,255):
   for value in (0,1,0x35,0xffffffff):
    for status in (0,0x2bad0000):
     observed=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
      for base,data in segments:u.mem_write(base,data)
      descriptor=0x20070f8c
      u.mem_write(descriptor,(0x20008abc).to_bytes(4,'little')+bytes([index]))
      calls=[]
      def lower(uc,at,size,user):
       target=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
       r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
       if target=='display_driver_uled_pmic_read_55fc38':
        calls.append(('read',r0,r1,r3));uc.mem_write(r2,b'\xa5');uc.reg_write(UC_ARM_REG_R0,status)
       elif target=='display_driver_uled_pmic_write_55fc2c':
        calls.append(('write',r0,r1,r3,bytes(uc.mem_read(r2,r3))));uc.reg_write(UC_ARM_REG_R0,0x66)
       else:
        calls.append(('commit',r0,r1));uc.reg_write(UC_ARM_REG_R0,0x77)
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      for n,at in callees:
       target=syms[n]&~1 if compiled else at
       u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      u.reg_write(UC_ARM_REG_R0,descriptor);u.reg_write(UC_ARM_REG_R1,value)
      u.emu_start((syms[name] if compiled else native)|1,0x600000,count=1000)
      observed.append((u.reg_read(UC_ARM_REG_R0),calls))
     assert observed[0]==observed[1],(name,index,value,status,observed)
     cases+=1
 print('PASS_ULED_OPTION_PMIC_HELPERS_NATIVE',cases)
