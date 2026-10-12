#!/usr/bin/env python3
"""Bounded native/C LV style property mutation: constant, replace, grow, OOM."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_local_value.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_lv_realloc_44f76a(void*a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_heap_alloc(uint32_t a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,const char*e,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_page_style_value_482868',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('constant','replace','grow','oom'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   style=0x2007f100;old=0x2007f200;new=0x2007f500
   u.mem_write(style,struct.pack('<IIB',old if mode=='replace' else 0,0,255 if mode=='constant' else (1 if mode=='replace' else 0))+b'\0'*3)
   u.mem_write(old,struct.pack('<I',0x12345678)+b'\x0a');u.mem_write(new,b'\xaa'*64)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,style);u.reg_write(UC_ARM_REG_R1,10 if mode=='replace' else 20);u.reg_write(UC_ARM_REG_R2,0x50607080)
   events=[]
   def hook(uc,a,size,_):
    if a in (0x44f76a,sym['audio_uart_lv_realloc_44f76a']&~1):
     events.append(('realloc',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,0 if mode=='oom' else new);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x44d25c,sym['audio_uart_lvgl_log']&~1):
     events.append(('log',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_page_style_value_482868'] if is_c else 0x482868)|1,0x600000,count=300)
   pair.append((events,bytes(u.mem_read(style,12)),bytes(u.mem_read(old,8)),bytes(u.mem_read(new,12))))
  assert pair[0]==pair[1],(mode,pair)
  cases+=1
 print('PASS_DISPLAY_LV_STYLE_VALUE_NATIVE',cases)
