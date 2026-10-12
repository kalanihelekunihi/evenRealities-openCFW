#!/usr/bin/env python3
"""All 256 native property-default branches with explicit incoming R1."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_property_default_model.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_property_default_48297c',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for seed in (0,0xa5000000,0xffffffff):
  for prop in range(256):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,prop);u.reg_write(UC_ARM_REG_R1,seed)
    if not is_c:
     def hook(uc,a,size,_):
      if a==0x43bb00:
       uc.mem_write(uc.reg_read(UC_ARM_REG_R0),b'\0'*uc.reg_read(UC_ARM_REG_R2));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      if a==0x439be4:
       uc.mem_write(uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_uart_lv_property_default_48297c'] if is_c else 0x48297c)|1,0x600000,count=300)
    pair.append(u.reg_read(UC_ARM_REG_R0))
   assert pair[0]==pair[1],(hex(prop),hex(seed),list(map(hex,pair)))
   cases+=1
 print('PASS_DISPLAY_LV_PROPERTY_DEFAULT_MODEL_NATIVE',cases)
