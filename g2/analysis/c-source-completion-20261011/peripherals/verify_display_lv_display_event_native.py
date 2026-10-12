#!/usr/bin/env python3
"""Actual ARM/C LV display event envelope and capture/bubble sequencing."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_display_event.c'
stub='''#include <stdint.h>
__attribute__((naked)) void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_event_list_dispatch_44ffe6(void*a,void*b,uint32_t c){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_display_event_44fdbe',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for result0 in (0,1):
  for result1 in (0,1):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    display=0x2007f100;param=0x2007f200
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,display);u.reg_write(UC_ARM_REG_R1,0x38);u.reg_write(UC_ARM_REG_R2,param)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x44f7b4,sym['audio_uart_buffer_zero']&~1):
      ptr=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);uc.mem_write(ptr,b'\0'*n);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x44ffe6,sym['audio_uart_lv_event_list_dispatch_44ffe6']&~1):
      phase=uc.reg_read(UC_ARM_REG_R2);evt=uc.reg_read(UC_ARM_REG_R1);seen.append((uc.reg_read(UC_ARM_REG_R0),phase,bytes(uc.mem_read(evt,0x1c))));uc.reg_write(UC_ARM_REG_R0,result0 if phase else result1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_uart_lv_display_event_44fdbe'] if is_c else 0x44fdbe)|1,0x600000,count=100)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0)&0xff))
   assert pair[0]==pair[1],(result0,result1,pair)
 print('PASS_DISPLAY_LV_DISPLAY_EVENT_NATIVE',4)
