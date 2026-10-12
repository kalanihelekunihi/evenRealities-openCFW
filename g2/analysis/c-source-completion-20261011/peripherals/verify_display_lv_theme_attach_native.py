#!/usr/bin/env python3
"""Native/C theme attachment and conditional three-layer validation."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_theme_attach.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_display_default_get(void){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(uint32_t a,const char*b,uint32_t c,const char*d,...){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_theme_check_44ddea(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_theme_apply_482f8a(void*a){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_page_44fe0e',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for use_default in (False,True):
  for enabled in (False,True):
   for failure in (-1,0,1,2):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     disp=0x2007f100;layers=0x2007f500;theme=0x2007f800
     u.mem_write(disp,bytes([0xaa]*0x310));u.mem_write(disp+0x2d4,struct.pack('<I',4 if enabled else 3));u.mem_write(disp+0x2b8,struct.pack('<I',layers))
     u.mem_write(layers,struct.pack('<III',0x2007f900,0x2007fa00,0x2007fb00))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if use_default else disp);u.reg_write(UC_ARM_REG_R1,theme)
     seen=[];checks=0
     def hook(uc,a,size,_):
      nonlocal_dummy=0
      if a in (0x44fa1a,sym['audio_uart_display_default_get']&~1):seen.append(('default',));uc.reg_write(UC_ARM_REG_R0,disp);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x44ddea,sym['audio_uart_lv_theme_check_44ddea']&~1):
       n=sum(x[0]=='check' for x in seen);seen.append(('check',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,1 if n==failure else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
      if a in (0x482f8a,sym['audio_uart_lv_theme_apply_482f8a']&~1):seen.append(('apply',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
     u.hook_add(UC_HOOK_CODE,hook)
     u.emu_start((sym['audio_uart_page_44fe0e'] if is_c else 0x44fe0e)|1,0x600000,count=350)
     pair.append((seen,bytes(u.mem_read(disp+0x300,4))))
    assert pair[0]==pair[1],(use_default,enabled,failure,pair)
    cases+=1
 print('PASS_DISPLAY_LV_THEME_ATTACH_NATIVE',cases)
