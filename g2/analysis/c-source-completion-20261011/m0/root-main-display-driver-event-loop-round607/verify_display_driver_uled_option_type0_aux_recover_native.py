#!/usr/bin/env python3
"""Compare bounded type-0 auxiliary recovery call order and argument passing."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_type0_context_46bfe8',0x46bfe8),('display_driver_uled_type0_context_snapshot_46c410',0x46c410),('display_driver_uled_type0_finish_59328c',0x59328c),('display_driver_uled_type0_pre_593200',0x593200),('display_driver_uled_type0_step_5927ca',0x5927ca),('display_driver_uled_type0_frame_lower_592dea',0x592dea),('display_driver_uled_type0_aux_config_592e9c',0x592e9c),('audio_ble_hci_radio_reset_4910f4',0x4910f4),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f){{return 0;}}' for name,at in callees))
 image=Path(directory)/'recover.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_option_type0_aux_recover.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for flags in (0,1,2,4,7):
  for pair in ((0x11223344,0x55667788),(0,0)):
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
     if name=='display_driver_uled_type0_context_46bfe8':calls.append((name,));result=0x20002000
     elif name=='display_driver_uled_type0_context_snapshot_46c410':
      calls.append((name,r0));uc.mem_write(r1,pair[0].to_bytes(4,'little'));uc.mem_write(r2,pair[1].to_bytes(4,'little'))
     elif name=='display_driver_uled_type0_frame_lower_592dea':
      sp=uc.reg_read(UC_ARM_REG_SP);calls.append((name,r0,r1,r2,r3,int.from_bytes(uc.mem_read(sp,4),'little'),int.from_bytes(uc.mem_read(sp+4,4),'little')))
     elif name=='display_driver_uled_type0_aux_config_592e9c':calls.append((name,r0,r1,r2))
     elif name=='audio_ble_hci_radio_reset_4910f4':calls.append((name,r0))
     elif name=='g2_flashdb_candidate_flags':calls.append((name,));result=flags
     elif name=='g2_flashdb_candidate_log':calls.append((name,r0,r1,r2,r3))
     elif name=='audio_log_simple':calls.append((name,r0,r1,r2))
     else:calls.append((name,))
     uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    for n,at in callees:
     target=syms[n]&~1 if compiled else at
     u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.emu_start((syms['display_driver_uled_type0_aux_recover_593528'] if compiled else 0x593528)|1,0x600000,count=3000)
    observed.append(calls)
   assert observed[0]==observed[1],(flags,pair,observed)
   cases+=1
 print('PASS_ULED_OPTION_TYPE0_AUX_RECOVER_NATIVE',cases)
