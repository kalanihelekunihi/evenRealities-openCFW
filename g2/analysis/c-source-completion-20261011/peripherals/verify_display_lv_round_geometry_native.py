#!/usr/bin/env python3
"""Actual compiled C/stock rectangle extent and circle predicate."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_round_geometry.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_area_width_451598',str(S),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name,native in [('audio_uart_lv_area_width_451598',0x451598),('audio_uart_lv_area_height_4515a4',0x4515a4),('audio_uart_lv_corner_arc_45163c',0x45163c)]:
  for box in ((0,0,10,10),(-5,2,6,9),(2,2,2,2),(10,9,0,0)):
   for point in ((0,0),(4,4),(10,10)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     a=0x2007f100;p=0x2007f200;u.mem_write(a,struct.pack('<4i',*box));u.mem_write(p,struct.pack('<2i',*point));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,p)
     u.emu_start((sym[name] if is_c else native)|1,0x600000,count=100);pair.append(u.reg_read(UC_ARM_REG_R0))
    assert pair[0]==pair[1],(name,box,point,list(map(hex,pair)))
    cases+=1
 print('PASS_DISPLAY_LV_ROUND_GEOMETRY_NATIVE',cases)
