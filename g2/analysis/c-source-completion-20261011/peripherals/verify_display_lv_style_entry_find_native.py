#!/usr/bin/env python3
"""Actual ARM/C LV object style-record property selection."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_entry_find.c'
stub='''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_page_style_selector_44b860(uint32_t a){__asm volatile("and.w r0,r0,#0xff0000; bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_style_entry_find_44c834',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for mode in ('match','miss','transition','states'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;entries=0x2007f200;style=0x2007f300;items=0x2007f400;out=0x2007f500
   for a,n in ((obj,64),(entries,32),(style,64),(items,64),(out,4)):u.mem_write(a,b'\0'*n)
   n=2 if mode=='states' else 1;u.mem_write(obj+12,struct.pack('<I',entries));u.mem_write(obj+0x2a,struct.pack('<H',n<<4))
   u.mem_write(style,struct.pack('<IIB',items,2,1));u.mem_write(items,struct.pack('<I',0x1111)+bytes([5]));
   tag=(0x02000000 if mode=='transition' else 0)|(0x10000 if mode=='miss' else 0)
   if mode=='states':u.mem_write(entries,struct.pack('<IIII',style,1,style,3))
   else:u.mem_write(entries,struct.pack('<II',style,tag))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,3 if mode=='states' else 0);u.reg_write(UC_ARM_REG_R2,5);u.reg_write(UC_ARM_REG_R3,out)
   u.emu_start((sym['audio_uart_lv_style_entry_find_44c834'] if is_c else 0x44c834)|1,0x600000,count=400)
   pair.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(out,4))))
  assert pair[0]==pair[1],(mode,pair)
 print('PASS_DISPLAY_LV_STYLE_ENTRY_FIND_NATIVE',4)
