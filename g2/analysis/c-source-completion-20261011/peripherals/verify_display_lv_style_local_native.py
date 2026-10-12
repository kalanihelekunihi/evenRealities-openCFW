#!/usr/bin/env python3
"""Actual ARM/C get_local_style existing and first allocation paths."""
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
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_page_style_local_44c5d4',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for existing in (False,True):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;entries=0x2007f500;style=0x2007f700;selector=0x12345
   u.mem_write(obj,b'\0'*64);u.mem_write(entries,b'\xaa'*32);u.mem_write(style,b'\xaa'*16)
   if existing:
    u.mem_write(obj+0x0c,struct.pack('<I',entries));u.mem_write(obj+0x2a,struct.pack('<H',0x10));u.mem_write(entries,struct.pack('<II',style,0x1000000|selector))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,selector)
   events=[]
   def hook(uc,a,size,_):
    if a in (0x44f76a,sym['audio_uart_lv_realloc_44f76a']&~1):events.append(('realloc',uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,entries);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x44f730,sym['audio_uart_lv_heap_alloc']&~1):events.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,style);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x44b7a8,0x48278c,sym['audio_uart_buffer_zero']&~1):
     ptr=uc.reg_read(UC_ARM_REG_R0);length=12 if a==0x48278c else uc.reg_read(UC_ARM_REG_R1)
     events.append(('zero',ptr,length));uc.mem_write(ptr,b'\0'*length);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_page_style_local_44c5d4'] if is_c else 0x44c5d4)|1,0x600000,count=300)
   pair.append((events,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(obj,64)),bytes(u.mem_read(entries,24)),bytes(u.mem_read(style,12))))
  assert pair[0]==pair[1],(existing,pair)
 print('PASS_DISPLAY_LV_STYLE_LOCAL_NATIVE',2)
