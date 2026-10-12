#!/usr/bin/env python3
"""Compare source/native recursive theme walker with chain callback intercepted."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_theme_apply.c'
stub='''#include <stdint.h>
__attribute__((naked)) void *audio_uart_display_default_get(void){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_display_for_object(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_style_remove_44ba9a(void*a,void*b,uint32_t c){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_theme_walk_482ff2',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for depth in (1,2):
  for flag in (0,0x100000):
   pairs=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    root=0x2007f100;child=0x2007f200;grand=0x2007f300;theme=0x2007f400
    u.mem_write(root,struct.pack('<I',child if depth else 0));u.mem_write(child,struct.pack('<I',grand if depth==2 else 0));u.mem_write(grand,b'\0'*4)
    u.mem_write(child+0x20,struct.pack('<I',flag));u.mem_write(grand+0x20,struct.pack('<I',0))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,theme);u.reg_write(UC_ARM_REG_R1,root)
    events=[];chain=sym['audio_uart_lv_theme_apply_chain_482fce']&~1
    def hook(uc,a,size,_):
     if a in (0x482fce,chain):
      obj=uc.reg_read(UC_ARM_REG_R1);events.append((uc.reg_read(UC_ARM_REG_R0),obj,struct.unpack('<I',uc.mem_read(obj,4))[0]));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    
    try:u.emu_start((sym['audio_uart_lv_theme_walk_482ff2'] if is_c else 0x482ff2)|1,0x600000,count=200)
    except Exception as exc:raise AssertionError((depth,flag,is_c,hex(u.reg_read(UC_ARM_REG_PC)),events)) from exc
    pairs.append((events,struct.unpack('<I',u.mem_read(root,4))[0]))
   assert pairs[0]==pairs[1],(depth,flag,pairs)
   cases+=1
 print('PASS_DISPLAY_LV_THEME_CHAIN_NATIVE',cases)
