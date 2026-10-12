#!/usr/bin/env python3
"""Actual ARM/C transition schedule pause/resume and timer update effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_transition_schedule.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_lv_list_first(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_timer_pause(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_transition_schedule_4509da',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for has_nodes in (False,True):
  for op in ('schedule','resume'):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    root=0x2006f548;timer=0x2007f100;u.mem_write(root+0x84,struct.pack('<I',0x1234));u.mem_write(root+0x9c,b'\0'*4);u.mem_write(root+0xa8,struct.pack('<I',timer));u.mem_write(timer,b'\0'*32);u.mem_write(timer+0x14,struct.pack('<I',3))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,timer)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x482cd8,sym['audio_uart_lv_list_first']&~1):seen.append(('first',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0x2007f200 if has_nodes else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     if a in (0x46450c,sym['audio_uart_lv_timer_pause']&~1):seen.append(('pause',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    u.hook_add(UC_HOOK_CODE,hook)
    nat,name=(0x4509da,'audio_uart_lv_transition_schedule_4509da') if op=='schedule' else (0x46453e,'audio_uart_lv_timer_resume_46453e')
    u.emu_start((sym[name] if is_c else nat)|1,0x600000,count=120)
    pair.append((seen,bytes(u.mem_read(root+0x84,4)),bytes(u.mem_read(root+0xa4,1)),bytes(u.mem_read(timer+0x14,4))))
   assert pair[0]==pair[1],(has_nodes,op,pair)
   cases+=1
 print('PASS_DISPLAY_LV_TRANSITION_SCHEDULE_NATIVE',cases)
