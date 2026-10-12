#!/usr/bin/env python3
"""Native/C LV active-screen getter and application-root call effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_application_root.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_display_default_get(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_application_init',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('get','root'):
  for direct in (False,True):
   for fallback in (False,True):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     disp=0x2007f100;screen=0x2007f500;u.mem_write(disp+0x2c4,struct.pack('<I',screen))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,disp if direct else 0)
     seen=[]
     def cstr(uc,p):return bytes(uc.mem_read(p,150)).split(b'\0')[0].decode('latin1')
     def hook(uc,a,size,_):
      if a in (0x44fa1a,sym['audio_uart_display_default_get']&~1):seen.append(('default',));uc.reg_write(UC_ARM_REG_R0,disp if fallback else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x44d25c,sym['audio_uart_lvgl_log']&~1):seen.append(('log',uc.reg_read(UC_ARM_REG_R0),cstr(uc,uc.reg_read(UC_ARM_REG_R1)),uc.reg_read(UC_ARM_REG_R2),cstr(uc,uc.reg_read(UC_ARM_REG_R3))));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     entry=sym['audio_uart_display_active_screen_get' if mode=='get' else 'audio_uart_display_application_init'] if is_c else (0x44fc62 if mode=='get' else 0x44ff38)
     u.emu_start(entry|1,0x600000,count=250)
     pair.append((seen,u.reg_read(UC_ARM_REG_R0)))
    assert pair[0]==pair[1],(mode,direct,fallback,pair)
    cases+=1
 print('PASS_DISPLAY_LV_APPLICATION_ROOT_NATIVE',cases)
