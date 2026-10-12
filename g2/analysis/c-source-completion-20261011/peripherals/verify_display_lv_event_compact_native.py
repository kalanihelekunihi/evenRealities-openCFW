#!/usr/bin/env python3
"""Actual ARM/C LV event descriptor compaction and array clear effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate';S=[D/'display_lv_event_compact.c',D/'display_lv_event_array.c']
stub='''#include <stdint.h>
__attribute__((naked)) void audio_uart_lv_heap_free(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_realloc_44f76a(void*a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_event_restore_4502e0',*[str(x) for x in S],str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for op in ('restore','compact'):
  for invalid in (False,True):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    li=0x2007f100;data=0x2007f200;d0=0x2007f300;d1=0x2007f400
    u.mem_write(li,struct.pack('<IIII',data,2,2,4)+bytes([0])+b'\0'*7);u.mem_write(li+0x14,b'\x02');u.mem_write(data,struct.pack('<II',d0,d1));u.mem_write(d0,struct.pack('<III',0,0,0x10000 if invalid else 0));u.mem_write(d1,struct.pack('<III',0,0,0))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,li)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x44f758,sym['audio_uart_lv_heap_free']&~1):seen.append(('free',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x48849c,sym['audio_uart_lv_array_resize_48849c']&~1):seen.append(('resize',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)));uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    nat,name=(0x4502e0,'audio_uart_lv_event_restore_4502e0') if op=='restore' else (0x450346,'audio_uart_lv_event_compact_450346')
    u.emu_start((sym[name] if is_c else nat)|1,0x600000,count=300)
    pair.append((seen,bytes(u.mem_read(li,24)),bytes(u.mem_read(data,8))))
   assert pair[0]==pair[1],(op,invalid,pair)
   cases+=1
 print('PASS_DISPLAY_LV_EVENT_COMPACT_NATIVE',cases)
