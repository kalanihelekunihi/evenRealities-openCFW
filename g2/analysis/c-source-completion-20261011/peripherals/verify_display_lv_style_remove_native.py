#!/usr/bin/env python3
"""Actual ARM/C style removal records and ordered lower effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_remove.c'
names=['audio_uart_page_style_selector_44b860','audio_uart_page_style_resolve_44ca18','audio_uart_display_size_changed','audio_uart_lv_style_has_flag_44ce2c','audio_uart_lv_style_reset_482796','audio_uart_lv_style_release_44f758','audio_uart_lv_realloc_44f76a','audio_uart_lv_style_removed_44ce2a','audio_uart_page_style_refresh_44bc8c']
addrs=[0x44b860,0x44ca18,0x440656,0x44ce2c,0x482796,0x44f758,0x44f76a,0x44ce2a,0x44bc8c]
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in names)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_style_remove_44ba9a',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('none','normal','local','transition','second'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;entries=0x2007f500;style=0x2007f700;other=0x2007f800
   u.mem_write(obj,b'\0'*64);u.mem_write(entries,b'\xaa'*32);u.mem_write(style,b'\0'*16)
   count=2 if mode=='second' else 1
   u.mem_write(obj+0x0c,struct.pack('<I',entries));u.mem_write(obj+0x2a,struct.pack('<H',count<<4))
   tag=0x123 | (0x1000000 if mode=='local' else 0x2000000 if mode=='transition' else 0)
   if mode=='none':tag=0x456
   if mode=='second':u.mem_write(entries,struct.pack('<II',other,0x456));u.mem_write(entries+8,struct.pack('<II',style,tag))
   else:u.mem_write(entries,struct.pack('<II',style,tag))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,0x123)
   seen=[];table={a:i for i,a in enumerate(addrs if not is_c else [sym[n]&~1 for n in names])}
   def hook(uc,a,size,_):
    if a in table:
     k=table[a];args=(uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2))
     if k!=0:seen.append((k,args[:3] if k in (1,8) else args[:2] if k in (3,6) else args[:1]))
     value=args[0]&0xff0000 if k==0 else entries if k==6 else 0
     uc.reg_write(UC_ARM_REG_R0,value);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_style_remove_44ba9a'] if is_c else 0x44ba9a)|1,0x600000,count=500)
   pair.append((seen,bytes(u.mem_read(obj,64)),bytes(u.mem_read(entries,24))))
  assert pair[0]==pair[1],(mode,pair)
  cases+=1
 print('PASS_DISPLAY_LV_STYLE_REMOVE_NATIVE',cases)
