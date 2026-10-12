#!/usr/bin/env python3
"""Actual ARM/C LV child count, parent and style propagation."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_tree.c'
stub='''#include <stdint.h>
__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_display_size_changed(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_obj_event_451670(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_refresh_children_44c9dc',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for operation in ('count','parent','refresh'):
  for children in (0,1):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    obj=0x2007f100;container=0x2007f500;slots=0x2007f600;child=0x2007f700
    u.mem_write(obj,b'\0'*64);u.mem_write(child,b'\0'*64);u.mem_write(container,b'\0'*64)
    u.mem_write(obj+4,struct.pack('<I',0x2007f900));u.mem_write(obj+8,struct.pack('<I',container if children else 0));u.mem_write(container,struct.pack('<I',slots));u.mem_write(container+0x30,struct.pack('<H',children));u.mem_write(slots,struct.pack('<I',child))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
    seen=[];targets={0x440656:0,0x451670:1} if not is_c else {sym['audio_uart_display_size_changed']&~1:0,sym['audio_uart_lv_obj_event_451670']&~1:1}
    def hook(uc,a,size,_):
     if a in targets:
      seen.append((targets[a],uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if targets[a] else 0));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    fn={'count':(0x44ddea,'audio_uart_lv_theme_check_44ddea'),'parent':(0x44dca2,'audio_uart_lv_obj_has_parent_44dca2'),'refresh':(0x44c9dc,'audio_uart_lv_refresh_children_44c9dc')}[operation]
    u.emu_start((sym[fn[1]] if is_c else fn[0])|1,0x600000,count=250)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0) if operation!='refresh' else 0))
   assert pair[0]==pair[1],(operation,children,pair)
   cases+=1
 print('PASS_DISPLAY_LV_STYLE_TREE_NATIVE',cases)
