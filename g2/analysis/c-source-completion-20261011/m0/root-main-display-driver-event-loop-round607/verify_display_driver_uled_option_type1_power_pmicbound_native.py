#!/usr/bin/env python3
"""Compare 0x5122ec C and native call/argument behavior with PMIC bounded."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('audio_ble_hci_radio_mode_state_50938e',0x50938e),('display_driver_uled_pmic_find_55fa0e',0x55fa0e),('display_driver_uled_pmic_enable_55fa40',0x55fa40),('display_driver_uled_pmic_voltage_55fa22',0x55fa22),('display_driver_uled_pmic_commit_55fa18',0x55fa18),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c'
 stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f){{return 0;}}' for name,at in callees))
 image=Path(directory)/'power.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type1_power_pmicbound.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in (0,6,255):
  for buck in (0,0x20009100):
   for flags in (0,1,2,4,7):
    observed=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
     u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
     for base,data in segments:u.mem_write(base,data)
     u.mem_write(0x20002000,bytes([mode]))
     calls=[]
     def lower(uc,at,size,user):
      name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
      arg_count={'audio_ble_hci_radio_mode_state_50938e':1,'display_driver_uled_pmic_find_55fa0e':2,'display_driver_uled_pmic_enable_55fa40':2,'display_driver_uled_pmic_voltage_55fa22':2,'display_driver_uled_pmic_commit_55fa18':2,'g2_flashdb_candidate_flags':0,'g2_flashdb_candidate_log':4,'audio_log_simple':3}[name]
      regs=(UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)
      calls.append((name,tuple(uc.reg_read(x) for x in regs[:arg_count])))
      result=0x20002000 if name=='audio_ble_hci_radio_mode_state_50938e' else buck if name=='display_driver_uled_pmic_find_55fa0e' else flags if name=='g2_flashdb_candidate_flags' else 0
      uc.reg_write(UC_ARM_REG_R0,result)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     for n,at in callees:
      target=syms[n]&~1 if compiled else at
      u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.emu_start((syms['display_driver_uled_type1_power_5122ec'] if compiled else 0x5122ec)|1,0x600000,count=2000)
     observed.append(calls)
    assert observed[0]==observed[1],(mode,buck,flags,observed)
    cases+=1
 print('PASS_ULED_OPTION_TYPE1_POWER_NATIVE',cases)
