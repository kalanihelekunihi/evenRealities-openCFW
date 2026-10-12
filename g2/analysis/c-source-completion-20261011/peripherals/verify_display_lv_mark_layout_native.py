#!/usr/bin/env python3
"""Actual ARM/C LV layout dirty bits and display event arguments."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_mark_layout.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_lv_object_screen(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_display_for_object(void*a){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_display_event_44fdbe(void*a,uint32_t b,void*c){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_mark_layout_43f648',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for same in (False,True):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;screen=obj if same else 0x2007f200;display=0x2007f300
   u.mem_write(obj,b'\0'*64);u.mem_write(screen,b'\0'*64)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
   seen=[];mapn={0x44dbc4:'screen',0x44dc0a:'display',0x44fdbe:'event'} if not is_c else {sym['audio_uart_lv_object_screen']&~1:'screen',sym['audio_uart_lv_display_for_object']&~1:'display',sym['audio_uart_lv_display_event_44fdbe']&~1:'event'}
   def hook(uc,a,size,_):
    if a in mapn:
     k=mapn[a];seen.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if k=='event' else 0,uc.reg_read(UC_ARM_REG_R2) if k=='event' else 0))
     uc.reg_write(UC_ARM_REG_R0,screen if k=='screen' else display if k=='display' else 1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_mark_layout_43f648'] if is_c else 0x43f648)|1,0x600000,count=70)
   pair.append((seen,bytes(u.mem_read(obj+0x2a,2)),bytes(u.mem_read(screen+0x2a,2))))
  assert pair[0]==pair[1],(same,pair)
 print('PASS_DISPLAY_LV_MARK_LAYOUT_NATIVE',2)
