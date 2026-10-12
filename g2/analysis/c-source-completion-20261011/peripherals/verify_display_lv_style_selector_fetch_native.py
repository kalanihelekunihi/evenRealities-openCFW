#!/usr/bin/env python3
"""Actual ARM/C selector property direct, inherited and special paths."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_selector_fetch.c'
stub='''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_page_style_selector_44b860(uint32_t a){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_style_entry_find_44c834(void*a,uint32_t b,uint8_t c,uint32_t*d){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_lv_builtin_property_flags=0x6d439c','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_selector_style_prop_44ce8a',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode,prop in (('direct',5),('none',5),('special',1),('inherit',39)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;parent=0x2007f200;out=0x2007f300;u.mem_write(obj,b'\0'*64);u.mem_write(parent,b'\0'*64);u.mem_write(out,struct.pack('<I',0))
   u.mem_write(obj,struct.pack('<I',parent));u.mem_write(obj+4,struct.pack('<I',parent));u.mem_write(parent+24,struct.pack('<I',0xabc))
   u.mem_write(parent+0x28,struct.pack('<H',0x31))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,prop);u.reg_write(UC_ARM_REG_R3,out)
   seen=[]
   def hook(uc,a,size,_):
    if a in (0x44b860,sym['audio_uart_page_style_selector_44b860']&~1):uc.reg_write(UC_ARM_REG_R0,uc.reg_read(UC_ARM_REG_R0)&0xff0000);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x44c834,sym['audio_uart_lv_style_entry_find_44c834']&~1):
     who=uc.reg_read(UC_ARM_REG_R0);seen.append((who,uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2)))
     found=mode=='direct' or mode=='inherit' and who==parent
     if found:uc.mem_write(uc.reg_read(UC_ARM_REG_R3),struct.pack('<I',0x1234))
     uc.reg_write(UC_ARM_REG_R0,int(found));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_selector_style_prop_44ce8a'] if is_c else 0x44ce8a)|1,0x600000,count=150)
   pair.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(out,4))))
  assert pair[0]==pair[1],(mode,pair)
  cases+=1
 print('PASS_DISPLAY_LV_STYLE_SELECTOR_FETCH_NATIVE',cases)
