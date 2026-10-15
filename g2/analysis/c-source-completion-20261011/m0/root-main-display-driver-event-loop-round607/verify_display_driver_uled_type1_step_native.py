#!/usr/bin/env python3
"""Compare bounded nonlogging Hongshi configure call sequence and state."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_uled_type0_context_46bfe8',0x46bfe8),('display_driver_uled_type0_context_snapshot_46c410',0x46c410),('display_driver_uled_type1_write_register_5bbdf0',0x5bbdf0),('display_driver_uled_type1_read_bank_5bbe80',0x5bbe80),('audio_ble_hci_boot_delay_491102',0x491102),('display_driver_uled_delay_449376',0x449376),('audio_ble_hci_radio_reset_4910f4',0x4910f4),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e),('display_driver_uled_type1_frame_start_5bcb28',0x5bcb28),('display_driver_uled_type1_set_brightness_5bc6ae',0x5bc6ae),('display_driver_uled_type1_set_offset_5bc4c0',0x5bc4c0)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'step.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_type1_step.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,brightness,bank,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for base,data in segments:u.mem_write(base,data)
  u.mem_write(0x200039c0,b'\x12\x34');calls=[]
  def lower(uc,at,size,user):
   name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   short=name.split('_')[-1]
   if short=='46bfe8':calls.append(('context',));result=brightness
   elif short=='46c410':
    calls.append(('snapshot',r[0]));uc.mem_write(r[1],(0x11223344).to_bytes(4,'little'));uc.mem_write(r[2],(0x55667788).to_bytes(4,'little'));result=0
   elif short=='5bbdf0':calls.append(('write',r[:3]));result=0
   elif short=='5bbe80':calls.append(('read',r[:2]));result=bank
   elif short in ('491102','449376','4910f4'):calls.append((short,r[0]));result=0
   elif name=='g2_flashdb_candidate_flags':result=flags
   elif name=='g2_flashdb_candidate_log':
    sp=uc.reg_read(UC_ARM_REG_SP);calls.append(('detail',r,tuple(int.from_bytes(uc.mem_read(sp+4*i,4),'little') for i in range(3))));result=0
   elif name=='audio_log_simple':calls.append(('compact',r));result=0
   elif short=='5bcb28':calls.append(('frame',));result=0
   elif short=='5bc6ae':calls.append(('brightness',r[:3]));result=0
   elif short=='5bc4c0':calls.append(('offset',r[:2]));result=0
   else:raise AssertionError(name)
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((syms['display_driver_uled_type1_step_5bbff2'] if compiled else 0x5bbff2)|1,0x600000,count=10000)
  return calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20074520,4))
 cases=0
 for brightness in (0,55):
  for bank in (0,2,0x36,0x3f,0xff):
   for flags in (0,1,2,4,7):
    native=run(False,brightness,bank,flags);source=run(True,brightness,bank,flags)
    assert native==source,(brightness,bank,flags,native,source)
    cases+=1
 print('PASS_ULED_TYPE1_STEP_NATIVE',cases)
