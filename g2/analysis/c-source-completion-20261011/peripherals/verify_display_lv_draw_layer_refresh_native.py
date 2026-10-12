#!/usr/bin/env python3
"""Actual ARM/C LV ext draw and layer refresh with controlled child effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_draw_layer_refresh.c'
ns=['audio_uart_lvgl_log','audio_uart_lv_obj_event_451670','audio_uart_lv_obj_setup_layer_43e1fa','audio_uart_display_size_changed','audio_uart_lv_obj_layer_type_44cd9e']
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in ns)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_refresh_draw_452d42',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for op in ('draw','layer'):
  for present in (False,True):
   for value in (0,3):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     obj=0x2007f100;layer=0x2007f200;u.mem_write(obj,b'\0'*64);u.mem_write(layer,b'\0'*64);u.mem_write(layer+0x2c,struct.pack('<I',1));u.mem_write(layer+0x32,struct.pack('<H',0xffff))
     if present:u.mem_write(obj+8,struct.pack('<I',layer))
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj)
     seen=[];nat=[0x44d25c,0x451670,0x43e1fa,0x440656,0x44cd9e];table={a:i for i,a in enumerate(nat if not is_c else [sym[n]&~1 for n in ns])}
     def hook(uc,a,size,_):
      if a in table:
       k=table[a];seen.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if k==1 else 0))
       if k==1:uc.mem_write(uc.reg_read(UC_ARM_REG_R2),struct.pack('<I',value))
       if k==2:uc.mem_write(obj+8,struct.pack('<I',layer))
       if k==4:uc.reg_write(UC_ARM_REG_R0,value)
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook)
     natfn,name=(0x452d42,'audio_uart_lv_refresh_draw_452d42') if op=='draw' else (0x44c50e,'audio_uart_lv_update_layer_44c50e')
     u.emu_start((sym[name] if is_c else natfn)|1,0x600000,count=150)
     pair.append((seen,bytes(u.mem_read(obj+8,4)),bytes(u.mem_read(layer+0x2c,8))))
    assert pair[0]==pair[1],(op,present,value,pair)
    cases+=1
 print('PASS_DISPLAY_LV_DRAW_LAYER_REFRESH_NATIVE',cases)
