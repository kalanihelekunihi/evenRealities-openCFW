#!/usr/bin/env python3
"""Actual compiled-C/stock area expansion and scrollbar ancestor predicate."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_visible_area_helpers.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_area_expand_450b98',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in range(8):
  for name,native in [('audio_uart_lv_area_expand_450b98',0x450b98),('audio_uart_lv_object_scrollbar_visible_440a18',0x440a18)]:
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    obj=0x2007f100;par=0x2007f200;spec=0x2007f300;area=0x2007f400;u.mem_write(obj,b'\0'*64);u.mem_write(par,b'\0'*64);u.mem_write(spec,b'\0'*64);u.mem_write(area,struct.pack('<4i',0,2,10,12));u.mem_write(obj+4,struct.pack('<I',par if mode&1 else 0));u.mem_write((par if mode&2 else obj)+8,struct.pack('<I',spec));u.mem_write(spec+0x32,struct.pack('<H',0x800 if mode&4 else 0))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,area if 'expand' in name else obj);u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_R2,mode+1)
    u.emu_start((sym[name] if is_c else native)|1,0x600000,count=100)
    pair.append((u.reg_read(UC_ARM_REG_R0) if 'expand' not in name else 0,bytes(u.mem_read(area,16))))
   assert pair[0]==pair[1],(name,mode,pair)
   cases+=1
 print('PASS_DISPLAY_LV_VISIBLE_HELPERS_NATIVE',cases)
