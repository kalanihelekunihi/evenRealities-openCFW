#!/usr/bin/env python3
"""Actual ARM/C LV array resize external and owned success domains."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_event_compact.c'
stub='''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_lv_event_count_450388(){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_event_slot_450390(){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_event_descriptor_invalid_45037e(){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_heap_free(){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_realloc_44f76a(){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_array_resize_48849c',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for owned in (0,1):
  for wanted in (1,4):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    li=0x2007f100;data=0x2007f200;new=0x2007f300;u.mem_write(li,struct.pack('<IIII',data,2,2,4)+bytes([owned])+b'\0'*7)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,li);u.reg_write(UC_ARM_REG_R1,wanted)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x44f76a,sym['audio_uart_lv_realloc_44f76a']&~1):seen.append(('realloc',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,new);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x44d25c,sym['audio_uart_lvgl_log']&~1):seen.append(('log',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R2)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_uart_lv_array_resize_48849c'] if is_c else 0x48849c)|1,0x600000,count=120)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(li,20))))
   assert pair[0]==pair[1],(owned,wanted,pair)
   cases+=1
 print('PASS_DISPLAY_LV_ARRAY_RESIZE_NATIVE',cases)
