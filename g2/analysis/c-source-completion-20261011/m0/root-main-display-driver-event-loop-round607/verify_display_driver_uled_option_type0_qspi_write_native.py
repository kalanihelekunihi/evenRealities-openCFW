#!/usr/bin/env python3
"""Compare bounded QSPI async write calls, transfer data, and result."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_packet_validate_59cb42',0x59cb42),('display_driver_uled_quad_mode_59ca2c',0x59ca2c),('display_driver_uled_interrupt_clear_4c23de',0x4c23de),('display_driver_uled_interrupt_enable_4c2328',0x4c2328),('display_driver_uled_prepare_transfer_47510e',0x47510e),('display_driver_uled_transfer_async_4c2208',0x4c2208),('audio_semaphore_acquire',0x44994e),('display_driver_uled_serial_mode_59c980',0x59c980),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'qspi.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_qspi_write.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for validation in (0,1):
  for acquired in (0,1,7):
   for flags in (0,1,2,4,7):
    observations=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     for a,value in ((0x2007453c,0x11112222),(0x20074538,0x33334444),(0x20074534,0x55556666)):
      u.mem_write(a,value.to_bytes(4,'little'))
     descriptor=bytearray(28)
     for offset,value in ((4,0x10203040),(12,0x50607080),(20,0x90a0b0c0),(24,0xd0e0f000)):
      descriptor[offset:offset+4]=value.to_bytes(4,'little')
     u.mem_write(0x20001000,bytes(descriptor))
     calls=[]
     def lower(uc,at,size,user):
      name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
      r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
      if name=='display_driver_uled_packet_validate_59cb42':result=validation;calls.append((name,r0,r1))
      elif name=='display_driver_uled_prepare_transfer_47510e':result=0;calls.append((name,bytes(uc.mem_read(r0,8))))
      elif name=='display_driver_uled_transfer_async_4c2208':result=0x1234;calls.append((name,r0,r2,r3,bytes(uc.mem_read(r1,24))))
      elif name=='audio_semaphore_acquire':result=acquired;calls.append((name,r0,r1))
      elif name=='g2_flashdb_candidate_flags':result=flags;calls.append((name,))
      else:result=0;calls.append((name,r0,r1,r2,r3))
      uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for name,at in callees:
      target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20001000)
     u.emu_start((syms['display_driver_uled_qspi_write_async_59ce1e'] if compiled else 0x59ce1e)|1,0x600000,count=3000)
     observations.append((calls,u.reg_read(UC_ARM_REG_R0)))
    assert observations[0]==observations[1],(validation,acquired,flags,observations)
    cases+=1
 print('PASS_ULED_OPTION_TYPE0_QSPI_WRITE_NATIVE',cases)
