#!/usr/bin/env python3
"""Compare native MSPI wait, shutdown, setup calls and state."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_wait_lower_538e8c',0x538e8c),('display_driver_uled_shutdown_lower_53909a',0x53909a),('display_driver_uled_setup_lower_538d58',0x538d58)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c){{return 0;}}' for name,at in callees))
 image=Path(directory)/'lifecycle.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_mspi_lifecycle.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for function,native in (('display_driver_uled_mspi_wait_4bfd62',0x4bfd62),('display_driver_uled_mspi_shutdown_4bfc86',0x4bfc86),('display_driver_uled_mspi_setup_4bfc5a',0x4bfc5a)):
  for module in (0,1,3):
   for saved_value in (0,0x11223344):
    observations=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     saved=0x200523d8+module*0x8d0+0x828
     u.mem_write(saved,saved_value.to_bytes(4,'little'))
     u.mem_write(0x20001004,module.to_bytes(4,'little'))
     u.mem_write(0x20001828,(0x55667788).to_bytes(4,'little'))
     calls=[]
     def lower(uc,at,size,user):
      name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
      r0,r1,r2=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2))
      if name=='display_driver_uled_setup_lower_538d58':calls.append((name,r0,bytes(uc.mem_read(r1,9)),r2))
      elif name=='display_driver_uled_shutdown_lower_53909a':calls.append((name,r0,r1))
      else:calls.append((name,r0))
      uc.reg_write(UC_ARM_REG_R0,0x778899aa if name=='display_driver_uled_wait_lower_538e8c' else 0)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for name,at in callees:
      target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     if function=='display_driver_uled_mspi_setup_4bfc5a':
      u.reg_write(UC_ARM_REG_R0,module);u.reg_write(UC_ARM_REG_R1,0xabcdef01);u.reg_write(UC_ARM_REG_R2,0x12345678)
     else:u.reg_write(UC_ARM_REG_R0,0x20001000)
     u.emu_start((syms[function] if compiled else native)|1,0x600000,count=1000)
     result=u.reg_read(UC_ARM_REG_R0) if function!='display_driver_uled_mspi_setup_4bfc5a' else None
     observations.append((calls,result,int.from_bytes(u.mem_read(saved,4),'little')))
    assert observations[0]==observations[1],(function,module,saved_value,observations)
    cases+=1
 print('PASS_ULED_OPTION_TYPE0_MSPI_LIFECYCLE_NATIVE',cases)
