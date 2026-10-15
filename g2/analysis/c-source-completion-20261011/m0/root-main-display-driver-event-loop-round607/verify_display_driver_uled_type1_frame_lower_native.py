#!/usr/bin/env python3
"""Compare Hongshi partial-refresh native and C call trace and QSPI descriptor."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e),('display_driver_uled_qspi_write_async_59ce1e',0x59ce1e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'frame.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_type1_frame_lower.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for handle in (0,0x12345678):
  for flags in (0,1,2,4,7):
   for dims in ((0,0),(639,479),(640,480),(900,900)):
    observations=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     u.mem_write(0x20074510,handle.to_bytes(4,'little'));u.mem_write(0x20074514,(0x87654321).to_bytes(4,'little'))
     calls=[]
     def copy(uc,at,size,user):
      dst=uc.reg_read(UC_ARM_REG_R0);src=uc.reg_read(UC_ARM_REG_R1);n=uc.reg_read(UC_ARM_REG_R2)
      uc.mem_write(dst,bytes(uc.mem_read(src,n)));uc.reg_write(UC_ARM_REG_R0,dst);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     if not compiled:u.hook_add(UC_HOOK_CODE,copy,begin=0x439c04,end=0x439c04)
     def lower(uc,at,size,user):
      name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
      regs=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
      if name=='g2_flashdb_candidate_flags':calls.append((name,));value=flags
      elif name=='display_driver_uled_qspi_write_async_59ce1e':calls.append((name,bytes(uc.mem_read(regs[0],28))));value=0x55
      elif name=='audio_log_simple':calls.append((name,regs[:3]));value=0
      else:calls.append((name,regs));value=0
      uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for name,at in callees:
      target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
     sp=0x200ff000;u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.mem_write(sp,dims[0].to_bytes(4,'little')+dims[1].to_bytes(4,'little'))
     u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,0)
     u.emu_start((syms['display_driver_uled_type1_frame_lower_5bcd44'] if compiled else 0x5bcd44)|1,0x600000,count=1000)
     observations.append((calls,u.reg_read(UC_ARM_REG_R0)))
    assert observations[0]==observations[1],(handle,flags,dims,observations)
    cases+=1
 print('PASS_ULED_TYPE1_FRAME_LOWER_NATIVE',cases)
