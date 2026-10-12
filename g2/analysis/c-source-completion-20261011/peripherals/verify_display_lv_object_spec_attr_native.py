#!/usr/bin/env python3
"""Actual ARM/C spec-attribute existing and allocation effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_object_spec_attr.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_lv_heap_alloc(uint32_t a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lvgl_log(){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_obj_setup_layer_43e1fa',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for existing in (False,True):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;layer=0x2007f200;u.mem_write(obj,b'\0'*64);u.mem_write(layer,b'\0'*0x34);u.mem_write(layer+0x32,struct.pack('<H',0x4000))
   if existing:u.mem_write(obj+8,struct.pack('<I',layer))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
   seen=[]
   def hook(uc,a,size,_):
    if a in (0x44f730,sym['audio_uart_lv_heap_alloc']&~1):seen.append(('alloc',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_R0,layer);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_obj_setup_layer_43e1fa'] if is_c else 0x43e1fa)|1,0x600000,count=100)
   pair.append((seen,bytes(u.mem_read(obj+8,4)),bytes(u.mem_read(layer+0x32,2))))
  assert pair[0]==pair[1],(existing,pair)
 print('PASS_DISPLAY_LV_OBJECT_SPEC_ATTR_NATIVE',2)
