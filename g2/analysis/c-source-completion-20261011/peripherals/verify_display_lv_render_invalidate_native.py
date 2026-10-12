#!/usr/bin/env python3
"""Bounded actual compiled-C/stock display invalidation effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_render_invalidate.c'
names=['audio_uart_display_default_get','audio_uart_lv_display_has_active_window','audio_uart_lv_display_width_44fa7e','audio_uart_lv_display_height_44faa8','audio_uart_lv_area_intersect_450bcc','audio_uart_lv_area_contains_450f28','audio_uart_lv_area_copy_4530fc','audio_uart_lv_display_event_44fdbe','audio_uart_lvgl_log']
native=[0x44fa1a,0x44fed2,0x44fa7e,0x44faa8,0x450bcc,0x450f28,0x4530fc,0x44fdbe,0x44d25c]
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in names)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_render_invalidate',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('missing','disabled','clear','outside','direct','event_stop','overlap','append','full'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   d=0x2007f100;inp=0x2007f800;u.mem_write(d,b'\0'*0x300);u.mem_write(inp,struct.pack('<4i',3,4,10,11));u.mem_write(d+0x260,struct.pack('<I',32 if mode=='full' else 1 if mode=='overlap' else 0));u.mem_write(d+0x39,bytes([2 if mode=='direct' else 1]));u.mem_write(d+0x3c,bytes([7 if mode=='append' else 0]))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0 if mode=='missing' else d);u.reg_write(UC_ARM_REG_R1,0 if mode=='clear' else inp)
   table={a:i for i,a in enumerate(native if not is_c else [sym[n]&~1 for n in names])};seen=[]
   def hook(uc,a,size,_):
    if a not in table:return
    k=table[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);seen.append((k,r0 if k in (1,2,3,7) else 0,r1 if k==7 else 0))
    if k==0: ret=0
    elif k==1: ret=0 if mode=='disabled' else 1
    elif k==2: ret=20
    elif k==3: ret=20
    elif k==4:
     uc.mem_write(r0,struct.pack('<4i',3,4,10,11));ret=0 if mode=='outside' else 1
    elif k==5:ret=1 if mode=='overlap' else 0
    elif k==6:uc.mem_write(r0,bytes(uc.mem_read(r1,16)));ret=0
    elif k==7:ret=0 if mode=='event_stop' and r1==0x35 else 1
    else:ret=0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_uart_lv_render_invalidate'] if is_c else 0x4534be)|1,0x600000,count=3000)
   pair.append((seen,bytes(u.mem_read(d+0x40,16)),bytes(u.mem_read(d+0x260,4))))
  assert pair[0]==pair[1],(mode,pair)
  cases+=1
 print('PASS_DISPLAY_LV_RENDER_INVALIDATE_NATIVE',cases)
