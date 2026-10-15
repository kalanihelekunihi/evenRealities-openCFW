#!/usr/bin/env python3
"""Bounded direct-native packet submit call-order and status comparison."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_lv_memzero_48949c',0x48949c),('display_driver_uled_packet_validate_59cb42',0x59cb42),('display_driver_uled_packet_begin_59c980',0x59c980),('display_driver_uled_packet_encode_59cafc',0x59cafc),('g2_norflash_transfer_4c2098',0x4c2098),('display_driver_uled_packet_end_59ca2c',0x59ca2c),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f){{return 0;}}' for name,at in callees))
 image=Path(directory)/'packet.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_packet_reused.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for validation in (0,1,0xffffffff):
  for submit in (0,2):
   for flags in (0,1,2,4,7):
    observed=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     u.mem_write(0x20074538,(0x20071300).to_bytes(4,'little'))
     u.mem_write(0x2007453c,(0x20071400).to_bytes(4,'little'))
     u.mem_write(0x20001018,(0x20074200).to_bytes(4,'little'))
     for base,data in segments:u.mem_write(base,data)
     calls=[]
     def lower(uc,at,size,user):
      name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
      r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
      if name=='audio_uart_lv_memzero_48949c':
       calls.append((name,r1));uc.mem_write(r0,bytes(r1))
      elif name=='display_driver_uled_packet_validate_59cb42':calls.append((name,r0,r1))
      elif name=='display_driver_uled_packet_begin_59c980' or name=='display_driver_uled_packet_end_59ca2c':calls.append((name,r0,r1))
      elif name=='display_driver_uled_packet_encode_59cafc':
       calls.append((name,r0,r2,bytes(uc.mem_read(r1,24))));uc.mem_write(r1,bytes(range(24)))
      elif name=='g2_norflash_transfer_4c2098':calls.append((name,r0,r2,bytes(uc.mem_read(r1,24))))
      elif name=='g2_flashdb_candidate_flags':calls.append((name,))
      elif name=='g2_flashdb_candidate_log':calls.append((name,r0,r1,r2,r3))
      else:calls.append((name,r0,r1,r2))
      uc.reg_write(UC_ARM_REG_R0,validation if name=='display_driver_uled_packet_validate_59cb42' else submit if name=='g2_norflash_transfer_4c2098' else flags if name=='g2_flashdb_candidate_flags' else 0)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for n,at in callees:
      target=syms[n]&~1 if compiled else at
      u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x20001000)
     u.emu_start((syms['display_driver_uled_type0_packet_59cc40'] if compiled else 0x59cc40)|1,0x600000,count=2000)
     observed.append((calls,u.reg_read(UC_ARM_REG_R0)))
    assert observed[0]==observed[1],(validation,submit,flags,observed)
    cases+=1
 print('PASS_ULED_OPTION_TYPE0_PACKET_REUSED_NATIVE',cases)
