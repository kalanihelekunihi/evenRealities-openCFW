#!/usr/bin/env python3
"""Differential check of Hongshi brightness mapping and register output."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
callees=[('display_driver_brightness_ratio_cell_4af73a',0x4af73a),('display_driver_uled_mode_45a568',0x45a568),('g2_flashdb_candidate_flags',0x43d0ce),('g2_flashdb_candidate_log',0x43d574),('audio_log_simple',0x43ce9e),('display_driver_uled_type1_write_register_5bbdf0',0x5bbdf0),('audio_ble_hci_radio_reset_4910f4',0x4910f4)]
with tempfile.TemporaryDirectory() as directory:
 stub=Path(directory)/'lower.c';stub.write_text('typedef unsigned u32;\n'+'\n'.join(f'u32 {name}(u32 a,u32 b,u32 c,u32 d,u32 e,u32 f,u32 g,u32 h){{return 0;}}' for name,at in callees))
 image=Path(directory)/'brightness.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-std=c11','-ffreestanding','-fno-builtin','-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_uled_type1_set_brightness.c'),str(stub),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as file:
  elf=ELFFile(file);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD'];syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,level,base,reduction,mode,flags):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
  u.mem_map(0x100000,0x200000);u.mem_map(0x20000000,0x100000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_write(0x20005000,bytes([base]));u.mem_write(0x20072da8+22,bytes([reduction,reduction]));calls=[]
  def lower(uc,at,size,user):
   if at==(syms['display_driver_uled_settings_get_config_46b44c']&~1 if compiled else 0x46b44c):name='config'
   else:name=next(n for n,a in callees if (syms[n]&~1 if compiled else a)==at)
   r=tuple(uc.reg_read(z) for z in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
   sp=uc.reg_read(UC_ARM_REG_SP)
   if name==callees[0][0]:calls.append(('nvdb',r[0]));result=0x20005000
   elif name==callees[1][0]:calls.append(('mode',));result=mode
   elif name=='config':result=0x20072da8
   elif name==callees[2][0]:result=flags
   elif name==callees[3][0]:calls.append(('detail',r,tuple(int.from_bytes(uc.mem_read(sp+4*i,4),'little') for i in range(3))));result=0
   elif name==callees[4][0]:calls.append(('compact',r,int.from_bytes(uc.mem_read(sp,4),'little')));result=0
   elif name==callees[5][0]:calls.append(('write',r[:3]));result=0
   else:calls.append(('reset',r[0]));result=0
   uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  for name,at in callees:
   target=syms[name]&~1 if compiled else at;u.hook_add(UC_HOOK_CODE,lower,begin=target,end=target)
  config_at=syms['display_driver_uled_settings_get_config_46b44c']&~1 if compiled else 0x46b44c
  u.hook_add(UC_HOOK_CODE,lower,begin=config_at,end=config_at)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,level&0xffffffff)
  u.emu_start((syms['display_driver_uled_type1_set_brightness_5bc6ae'] if compiled else 0x5bc6ae)|1,0x600000,count=10000)
  return calls
 cases=0
 for level in (-1,0,1,2,40,100,101,255):
  for base in (0,100,255):
   for reduction in (0,7,15):
    for mode in (0,1,2):
     for flags in (0,1,2,4,7):
      native=run(False,level,base,reduction,mode,flags);source=run(True,level,base,reduction,mode,flags)
      assert native==source,((level,base,reduction,mode,flags),native,source)
      cases+=1
 print('PASS_ULED_TYPE1_BRIGHTNESS_NATIVE',cases)
