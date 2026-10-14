#!/usr/bin/env python3
"""Compare Apollo wear gate through native settings accessor chain and ARM C."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_SP,UC_ARM_REG_LR
here=Path(__file__).resolve().parent
blob=(here.parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
 image=Path(d)/'wear.elf'
 subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb',
  '-O2','-nostdlib','-Wl,-Ttext=0x100000',str(here/'display_driver_wear_detect.c'),
  str(here/'display_driver_settings_live.c'),'-o',str(image)],check=True,capture_output=True)
 with image.open('rb') as f:
  elf=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in elf.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
 count=0
 for input_switch in (0,1,255):
  for mode in (0,2,3):
   observations=[]
   for compiled in (False,True):
    cpu=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS)
    cpu.mem_map(0x400000,0x400000);cpu.mem_write(0x438000,blob)
    cpu.mem_map(0x100000,0x200000);cpu.mem_map(0x20000000,0x100000)
    for address,data in segments:cpu.mem_write(address,data)
    settings=syms['audio_settings_config_live'] if compiled else 0x20072da8
    state=syms['display_driver_wear_mode_cell'] if compiled else 0x20074edc
    cpu.mem_write(settings+0x14,bytes([input_switch]))
    cpu.mem_write(state,mode.to_bytes(4,'little'))
    cpu.reg_write(UC_ARM_REG_SP,0x200ff000);cpu.reg_write(UC_ARM_REG_LR,0x600001)
    start=syms['display_driver_wear_detect_49eb96'] if compiled else 0x49eb96
    cpu.emu_start(start|1,0x600000,count=100)
    observations.append(cpu.reg_read(UC_ARM_REG_R0))
   assert observations[0]==observations[1],(input_switch,mode,observations)
   count+=1
print('PASS_DISPLAY_DRIVER_WEAR_DETECT_NATIVE',count)
