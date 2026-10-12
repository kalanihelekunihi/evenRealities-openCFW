#!/usr/bin/env python3
"""Actual ARM C/stock rounded area branch and corner-effect comparison."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_round_corner.c'
ns=['audio_uart_lv_area_width_451598','audio_uart_lv_area_height_4515a4','audio_uart_lv_corner_arc_45163c']
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in ns)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_round_corner_450dd4',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for point in ((-1,2),(0,0),(1,1),(2,2),(5,0),(5,5),(9,9),(10,5),(4,8)):
  for radius in (0,1,3,7):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    area=0x2007f100;pt=0x2007f200;u.mem_write(area,struct.pack('<4i',0,0,10,10));u.mem_write(pt,struct.pack('<2i',*point))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,area);u.reg_write(UC_ARM_REG_R1,pt);u.reg_write(UC_ARM_REG_R2,radius)
    table={a:i for i,a in enumerate([0x451598,0x4515a4,0x45163c] if not is_c else [sym[n]&~1 for n in ns])};seen=[]
    def hook(uc,a,size,_):
     if a not in table:return
     k=table[a];p=uc.reg_read(UC_ARM_REG_R0)
     if k<2:
      x0,y0,x1,y1=struct.unpack('<4i',bytes(uc.mem_read(p,16)));ret=(x1-x0+1) if k==0 else (y1-y0+1);seen.append((k,ret))
     else:
      rect=struct.unpack('<4i',bytes(uc.mem_read(p,16)));seen.append((k,rect));ret=1 if (sum(rect)&1)==0 else 0
     uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_uart_lv_round_corner_450dd4'] if is_c else 0x450dd4)|1,0x600000,count=800)
    pair.append((u.reg_read(UC_ARM_REG_R0),seen))
   assert pair[0]==pair[1],(point,radius,pair)
   cases+=1
 print('PASS_DISPLAY_LV_ROUND_CORNER_NATIVE',cases)
