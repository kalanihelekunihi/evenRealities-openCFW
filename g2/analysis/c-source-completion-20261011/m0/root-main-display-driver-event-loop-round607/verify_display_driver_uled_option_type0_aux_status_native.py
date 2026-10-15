#!/usr/bin/env python3
"""Compare direct-native S200 auxiliary status branches to C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_uart_buffer_zero',0x43c0e4),('display_driver_uled_type0_read_59275e',0x59275e),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f){{return 0;}}' for name,at in callees))
 image=Path(directory)/'status.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_aux_status.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for scenario in ('first_error','first_90','second_error','second_zero','success'):
  for flags in (0,1,2,4,7):
   observed=[]
   for compiled in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
    u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
    for base,data in segments:u.mem_write(base,data)
    calls=[]
    def lower(uc,at,size,user):
     name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
     r0,r1,r2,r3=(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
     result=0
     if name=='audio_uart_buffer_zero':calls.append((name,r1,r2));uc.mem_write(r0,bytes(r1))
     elif name=='display_driver_uled_type0_read_59275e':
      calls.append((name,r0,r2));uc.mem_write(r1,bytes([0x90 if scenario=='first_90' and r0==5 else 0 if scenario=='second_zero' and r0==0x35 else 0x12]))
      result=3 if scenario=='first_error' and r0==5 else 5 if scenario=='second_error' and r0==0x35 else 0
     elif name=='g2_flashdb_candidate_flags':calls.append((name,));result=flags
     elif name=='g2_flashdb_candidate_log':calls.append((name,r0,r1,r2,r3))
     else:calls.append((name,r0,r1,r2))
     uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for n,at in callees:
     target=syms[n]&~1 if compiled else at
     u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,1)
    u.emu_start((syms['display_driver_uled_type0_aux_status_593398'] if compiled else 0x593398)|1,0x600000,count=3000)
    observed.append((calls,u.reg_read(UC_ARM_REG_R0)))
   assert observed[0]==observed[1],(scenario,flags,observed)
   cases+=1
 print('PASS_ULED_OPTION_TYPE0_AUX_STATUS_NATIVE',cases)
