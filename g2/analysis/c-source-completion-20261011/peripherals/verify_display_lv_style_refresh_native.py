#!/usr/bin/env python3
"""Actual ARM/C style refresh effects for selected selector, property, flag domains."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_refresh.c'
funcs=['audio_uart_lvgl_log','audio_uart_display_size_changed','audio_uart_page_style_selector_44b860','audio_uart_page_style_needs_invalidate_44b844','audio_uart_lv_style_position_a_44b870','audio_uart_lv_style_position_b_44b866','audio_uart_lv_obj_event_451670','audio_uart_lv_mark_layout_43f648','audio_uart_lv_obj_has_parent_44dca2','audio_uart_lv_update_layer_44c50e','audio_uart_lv_refresh_draw_452d42','audio_uart_lv_refresh_children_44c9dc']
native=[0x44d25c,0x440656,0x44b860,0x44b844,0x44b870,0x44b866,0x451670,0x43f648,0x44dca2,0x44c50e,0x452d42,0x44c9dc]
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+f+'(){__asm volatile("bx lr");}\n' for f in funcs)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_page_style_refresh_44bc8c',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for enabled in (0,1):
  for selector in (0,0x10000,0x20000,0xf0000):
   for prop,flags in ((0xff,0),(5,0),(5,1),(5,2),(5,4),(5,16),(5,7)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     u.mem_write(0x2006f548+0x24,bytes([enabled]));obj=0x2007f100
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,selector);u.reg_write(UC_ARM_REG_R2,prop)
     seen=[];table={a:i for i,a in enumerate(native if not is_c else [sym[n]&~1 for n in funcs])}
     def hook(uc,a,size,_):
      if a in table:
       k=table[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
       seen.append((k,r0,r1,r2) if k in (6,) else (k,r0,r1) if k in (3,4,5) else (k,r0) if k in (1,2,7,8,9,10,11) else (k,))
       value=selector&0xff0000 if k==2 else int(bool(flags&r1)) if k==3 else 0x3fffffff if k in (4,5) else 0x2007f900 if k==8 else 0
       uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['audio_uart_page_style_refresh_44bc8c'] if is_c else 0x44bc8c)|1,0x600000,count=300)
     pair.append(seen)
    assert pair[0]==pair[1],(enabled,hex(selector),prop,flags,pair)
    cases+=1
 print('PASS_DISPLAY_LV_STYLE_REFRESH_NATIVE',cases)
