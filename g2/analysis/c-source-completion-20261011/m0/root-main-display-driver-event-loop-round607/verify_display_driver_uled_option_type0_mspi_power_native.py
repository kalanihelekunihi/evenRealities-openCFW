#!/usr/bin/env python3
"""Compare bounded MSPI enable/disable memory, calls, and return codes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_mspi_wait_4bfd62',0x4bfd62),('display_driver_uled_mspi_shutdown_4bfc86',0x4bfc86),('display_driver_uled_delay_4807a0',0x4807a0),('display_driver_uled_mspi_setup_4bfc5a',0x4bfc5a)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c){{return 0;}}' for name,at in callees))
 image=Path(directory)/'power.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_mspi_power.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=[('disable','null'),('disable','invalid'),('disable','already'),('disable','busy'),('disable','waitfail'),('disable','release'),('disable','no_release'),('enable','null'),('enable','invalid'),('enable','unconfigured'),('enable','simple'),('enable','setup')]
 for function,variant in cases:
  observations=[]
  for compiled in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
   u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000);u.mem_map(0x40060000,0x10000)
   for base,data in segments:u.mem_write(base,data)
   data=bytearray(0x900)
   def word(offset,value):data[offset:offset+4]=value.to_bytes(4,'little')
   word(0,0x01bebebe|(0x02000000 if function=='disable' and variant!='already' else 0))
   word(4,0);word(0x8cc,0x12345678);word(20,0x1111);word(24,1 if variant in ('waitfail','release','no_release','setup') else 0)
   if variant=='invalid':word(0,0)
   if variant=='unconfigured':data[8]=0
   else:data[8]=1
   if variant=='busy':word(0x840,1)
   u.mem_write(0x20001000,bytes(data))
   u.mem_write(0x40060090,(1 if variant=='release' else 0).to_bytes(4,'little'))
   calls=[]
   def lower(uc,at,size,user):
    name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
    args=tuple(uc.reg_read(reg) for reg in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
    calls.append((name,args[:3] if name=='display_driver_uled_mspi_setup_4bfc5a' else args[:1]))
    uc.reg_write(UC_ARM_REG_R0,5 if name=='display_driver_uled_mspi_wait_4bfd62' and variant=='waitfail' else 0)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   for name,at in callees:
    target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0 if variant=='null' else 0x20001000)
   name='display_driver_uled_mspi_'+function+'_4c0ea8' if function=='disable' else 'display_driver_uled_mspi_enable_4c0e1e'
   native=0x4c0ea8 if function=='disable' else 0x4c0e1e
   u.emu_start((syms[name] if compiled else native)|1,0x600000,count=3000)
   observations.append((calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20001000,0x900)),bytes(u.mem_read(0x40060000,0x400))))
  assert observations[0]==observations[1],(function,variant,observations[0][:2],observations[1][:2])
 print('PASS_ULED_OPTION_TYPE0_MSPI_POWER_NATIVE',len(cases))
