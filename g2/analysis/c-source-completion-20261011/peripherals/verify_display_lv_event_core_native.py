#!/usr/bin/env python3
"""Actual ARM C/stock event core branch and recursive callback effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_event_core.c'
ns=['audio_uart_lv_active_input_452ef8','audio_uart_lv_event_list_dispatch_44ffe6','audio_uart_lv_object_event_base_4516f8','audio_uart_lv_obj_has_parent_44dca2','audio_uart_lv_event_is_bubbled_451b34']
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in ns)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_event_core_451a6c',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for active,flags,fail,parent_on in ((0,0,0,0),(1,0,0,0),(1,1,0,0),(1,2,0,0),(0,1,0,0),(0,2,0,0),(0,0,1,0),(0,0,2,0),(0,0,3,0),(0,0,0,1)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   ev=0x2007f100;obj=0x2007f200;spec=0x2007f300;par=0x2007f400;u.mem_write(ev,b'\0'*32);u.mem_write(obj,b'\0'*64);u.mem_write(spec,b'\0'*64);u.mem_write(par,b'\0'*64);u.mem_write(ev,struct.pack('<I',obj));u.mem_write(ev+24,bytes([flags]));u.mem_write(obj+8,struct.pack('<I',spec));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ev)
   table={a:i for i,a in enumerate([0x452ef8,0x44ffe6,0x4516f8,0x44dca2,0x451b34] if not is_c else [sym[n]&~1 for n in ns])};seen=[];dispatch=[0]
   def hook(uc,a,size,_):
    if a not in table:return
    k=table[a];r0=uc.reg_read(UC_ARM_REG_R0);r2=uc.reg_read(UC_ARM_REG_R2);seen.append((k,r0 if k==1 else 0,r2 if k==1 else 0))
    if k==0:ret=1 if active else 0
    elif k==1:
     dispatch[0]+=1;ret=0 if fail in (1,3) and dispatch[0]==(1 if fail==1 else 2) else 1
    elif k==2:ret=0 if fail==2 else 1
    elif k==3:ret=par if parent_on and r0==obj else 0
    else:ret=1 if parent_on else 0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_uart_lv_event_core_451a6c'] if is_c else 0x451a6c)|1,0x600000,count=600)
   pair.append((u.reg_read(UC_ARM_REG_R0),seen,struct.unpack('<I',bytes(u.mem_read(ev,4)))[0]))
  assert pair[0]==pair[1],(active,flags,fail,parent_on,pair)
  cases+=1
 print('PASS_DISPLAY_LV_EVENT_CORE_NATIVE',cases)
