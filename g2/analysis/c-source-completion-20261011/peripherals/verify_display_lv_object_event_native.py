#!/usr/bin/env python3
"""Pinned LVGL C event body versus stock, compare named fields and calls."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_object_event.c'
ns=['audio_uart_lv_event_scope_begin_44ffd0','audio_uart_lv_event_core_451a6c','audio_uart_lv_event_scope_end_44ffdc']
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in ns)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_obj_event_451670',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for object in (0,0x2007f100):
  for code in (0,0x35,0x1234):
   for ret in (0,1,0x102):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     u.mem_write(0x200fe000,b'\xa5'*0x1000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,object);u.reg_write(UC_ARM_REG_R1,code);u.reg_write(UC_ARM_REG_R2,0x2007f300)
     table={a:i for i,a in enumerate([0x44ffd0,0x451a6c,0x44ffdc] if not is_c else [sym[n]&~1 for n in ns])};seen=[]
     def hook(uc,a,size,_):
      if a not in table:return
      k=table[a];e=uc.reg_read(UC_ARM_REG_R0);blob=bytes(uc.mem_read(e,28));words=struct.unpack('<6I',blob[:24]);seen.append((k,words[:5],blob[24]))
      if k==0:uc.mem_write(e+20,struct.pack('<I',0x2007f500))
      if k==1:uc.reg_write(UC_ARM_REG_R0,ret)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_uart_lv_obj_event_451670'] if is_c else 0x451670)|1,0x600000,count=150)
     pair.append((u.reg_read(UC_ARM_REG_R0),seen))
    assert pair[0]==pair[1],(object,code,ret,pair)
    cases+=1
 print('PASS_DISPLAY_LV_OBJECT_EVENT_NATIVE',cases)
