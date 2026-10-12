#!/usr/bin/env python3
"""Compiled-C/stock LV point transform, no-angle branch and identity branch."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_transform_points.c'
TRIG=R/'components/audio/uart_thread_source_candidate/display_lv_trig.c'
with tempfile.TemporaryDirectory() as td:
 t=Path(td);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_transform_area_4513c8',str(S),str(TRIG),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,256,256),(0,128,384),(0,1,1),(0,-256,256),(0,0,256),(450,256,256),(900,128,384),(1350,256,128),(-450,128,384)]
 for angle,sx,sy in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   pts=0x2007f000;pv=0x2007f100;sp=0x200ff000
   u.mem_write(pts,struct.pack('<8i',-20,3,4,8,17,-9,100,120));u.mem_write(pv,struct.pack('<2i',5,-7))
   u.mem_write(sp,struct.pack('<III',sy,pv,1))
   u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,pts);u.reg_write(UC_ARM_REG_R1,4);u.reg_write(UC_ARM_REG_R2,angle&0xffffffff);u.reg_write(UC_ARM_REG_R3,sx&0xffffffff)
   u.emu_start((sym['audio_uart_lv_transform_area_4513c8'] if is_c else 0x4513c8)|1,0x600000,count=5000)
   pair.append(bytes(u.mem_read(pts,32)))
  assert pair[0]==pair[1],(angle,sx,sy,pair)
 for angle in range(360):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,angle)
   u.emu_start((sym['audio_uart_lv_sin_4885f0'] if is_c else 0x4885f0)|1,0x600000,count=2000)
   pair.append(u.reg_read(UC_ARM_REG_R0))
  assert pair[0]==pair[1],(angle,pair)
 print('PASS_DISPLAY_LV_TRANSFORM_POINTS_NATIVE',len(cases)+360)
