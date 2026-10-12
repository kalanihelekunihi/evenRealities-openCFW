#!/usr/bin/env python3
"""Actual ARM/C 256-property LV flags matrix, with and without extension."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_property_flags.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_lv_builtin_property_flags=0x6d439c','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_property_flags_482a6a',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for extension in (False,True):
  for prop in range(256):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    if extension:
     u.mem_write(0x2006f548+0x28,struct.pack('<I',16));u.mem_write(0x2006f548+0x30,struct.pack('<I',0x2007f100));u.mem_write(0x2007f100,bytes(range(16)))
    else:u.mem_write(0x2006f548+0x30,b'\0'*4)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,prop)
    u.emu_start((sym['audio_uart_lv_property_flags_482a6a'] if is_c else 0x482a6a)|1,0x600000,count=60)
    pair.append(u.reg_read(UC_ARM_REG_R0)&0xff)
   assert pair[0]==pair[1],(extension,prop,pair)
   cases+=1
 print('PASS_DISPLAY_LV_STYLE_PROPERTY_FLAGS_NATIVE',cases)
