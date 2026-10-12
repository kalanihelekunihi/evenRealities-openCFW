#!/usr/bin/env python3
"""Compare compiled C and stock 0x440494 with the authenticated null-object branch.

Non-null scrollbar mode and active clipping depend on 0x452dd8/0x440dda and
remain outside this bounded oracle.
"""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_scrollbar_clip.c'
STUB='''#include <stdint.h>
void *audio_uart_lv_obj_has_parent_44dca2(void *p){(void)p;return 0;}
void audio_uart_lv_scrollbar_clip_child_440dda(void *p,int32_t *a,uint32_t b,uint32_t c){(void)p;(void)a;(void)b;(void)c;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_object_scrollbar_area_440494',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,0,10,10),(3,4,3,4),(-8,-5,8,5),(20,11,2,-7),(-2,-1,-1,2),(0,0,-1,-1)]
 for values in cases:
  outputs=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   area=0x2007f400;u.mem_write(area,struct.pack('<4i',*values))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0);u.reg_write(UC_ARM_REG_R1,area);u.reg_write(UC_ARM_REG_R2,1)
   u.emu_start((sym['audio_uart_lv_object_scrollbar_area_440494'] if is_c else 0x440494)|1,0x600000,count=1000)
   outputs.append(bytes(u.mem_read(area,16)))
  assert outputs[0]==outputs[1],(values,outputs)
 for bits in (0,1,2,3):
  outputs=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;spec=0x2007f200
   u.mem_write(obj+8,struct.pack('<I',spec));u.mem_write(spec+0x32,struct.pack('<H',bits<<10))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
   u.emu_start((sym['audio_uart_lv_scrollbar_mode_452dd8'] if is_c else 0x452dd8)|1,0x600000,count=100)
   outputs.append(u.reg_read(UC_ARM_REG_R0))
  assert outputs[0]==outputs[1],(bits,outputs)
 print('PASS_DISPLAY_LV_SCROLLBAR_CLIP_NATIVE',len(cases)+4)
