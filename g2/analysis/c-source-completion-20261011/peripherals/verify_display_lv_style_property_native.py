#!/usr/bin/env python3
"""Actual ARM/C LV style property selector, seed and default fallback."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_property.c'
stub='''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_lv_selector_style_prop_44ce8a(void*a,uint32_t b,uint32_t c,uint32_t*d){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_property_default_48297c(uint32_t a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_style_property_44bdea',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for found in (False,True):
  for property in (1,255):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    obj=0x2007f100;u.mem_write(obj,b'\0'*64);u.mem_write(obj+0x28,struct.pack('<H',0x31))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,0x10000);u.reg_write(UC_ARM_REG_R2,property)
    seen=[]
    def hook(uc,a,size,_):
     if a in (0x44ce8a,sym['audio_uart_lv_selector_style_prop_44ce8a']&~1):
      seen.append(('fetch',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),struct.unpack('<I',uc.mem_read(uc.reg_read(UC_ARM_REG_R3),4))[0]));uc.mem_write(uc.reg_read(UC_ARM_REG_R3),struct.pack('<I',0x12345678));uc.reg_write(UC_ARM_REG_R0,int(found));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     if a in (0x48297c,sym['audio_uart_lv_property_default_48297c']&~1):
      seen.append(('default',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,0x9abcdef0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_uart_lv_style_property_44bdea'] if is_c else 0x44bdea)|1,0x600000,count=120)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(found,property,pair)
   cases+=1
 print('PASS_DISPLAY_LV_STYLE_PROPERTY_NATIVE',cases)
