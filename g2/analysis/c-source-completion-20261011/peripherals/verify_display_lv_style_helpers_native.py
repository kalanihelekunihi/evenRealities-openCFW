#!/usr/bin/env python3
"""Actual ARM/C mutable and constant LV style flag scans, reset effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_helpers.c'
stub='''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_page_style_needs_invalidate_44b844(uint32_t a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_heap_free(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_style_has_flag_44ce2c',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for constant in (False,True):
  for match in (False,True):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    s=0x2007f100;v=0x2007f200;u.mem_write(s,struct.pack('<IIB',v,0,255 if constant else 2)+b'\0'*3)
    u.mem_write(v,b'\0'*40)
    if constant:u.mem_write(v,bytes([7 if match else 6])+b'\0'*7+b'\0')
    else:u.mem_write(v+8,bytes([6,7 if match else 6]))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,s);u.reg_write(UC_ARM_REG_R1,0x20)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x44b844,sym['audio_uart_page_style_needs_invalidate_44b844']&~1):
      prop=uc.reg_read(UC_ARM_REG_R0);seen.append(prop);uc.reg_write(UC_ARM_REG_R0,int(prop==7));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_uart_lv_style_has_flag_44ce2c'] if is_c else 0x44ce2c)|1,0x600000,count=100)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(constant,match,pair)
   cases+=1
 print('PASS_DISPLAY_LV_STYLE_HELPERS_NATIVE',cases)
