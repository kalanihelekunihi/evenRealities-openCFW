#!/usr/bin/env python3
"""Actual ARM/C mutable/constant LV style property removal."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_remove_prop.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_lv_malloc(uint32_t a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_heap_free(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_style_notify_4827b0',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for mode in ('constant','miss','first','second','oom'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   s=0x2007f100;old=0x2007f200;new=0x2007f300;u.mem_write(s,struct.pack('<IIB',old,2,255 if mode=='constant' else 2)+b'\0'*3)
   u.mem_write(old,struct.pack('<II',0x1111,0x2222)+bytes([5,7])+b'\0'*30);u.mem_write(new,b'\xaa'*40)
   prop=9 if mode=='miss' else 7 if mode=='second' else 5
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,s);u.reg_write(UC_ARM_REG_R1,prop)
   seen=[]
   def hook(uc,a,size,_):
    if a in (0x44f718,sym['audio_uart_lv_malloc']&~1):seen.append(('malloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0 if mode=='oom' else new);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x44f758,sym['audio_uart_lv_heap_free']&~1):seen.append(('free',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x44d25c,sym['audio_uart_lvgl_log']&~1):seen.append(('log',uc.reg_read(UC_ARM_REG_R2)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_style_notify_4827b0'] if is_c else 0x4827b0)|1,0x600000,count=250)
   pair.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(s,12)),bytes(u.mem_read(new,12))))
  assert pair[0]==pair[1],(mode,pair)
 print('PASS_DISPLAY_LV_STYLE_REMOVE_PROP_NATIVE',5)
