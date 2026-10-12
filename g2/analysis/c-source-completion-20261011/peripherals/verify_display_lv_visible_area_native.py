#!/usr/bin/env python3
"""Bounded compiled C/stock visible-area branch and rectangle effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_visible_area.c'
names=['audio_uart_lv_obj_has_flag_43e0e0','audio_uart_lv_object_screen','audio_uart_lv_display_for_object','audio_uart_display_active_screen_get','audio_uart_lv_display_previous_screen_44fc90','audio_uart_lv_display_bottom_layer_44fd38','audio_uart_lv_display_top_layer_44fcbe','audio_uart_lv_display_system_layer_44fcfc','audio_uart_lv_draw_size_get_452dc8','audio_uart_lv_area_copy_4530fc','audio_uart_lv_area_expand_450b98','audio_uart_lv_area_intersect_450bcc','audio_uart_lv_object_scrollbar_visible_440a18','audio_uart_lv_object_scrollbar_area_440494','audio_uart_lv_obj_has_parent_44dca2']
native=[0x43e0e0,0x44dbc4,0x44dc0a,0x44fc62,0x44fc90,0x44fd38,0x44fcbe,0x44fcfc,0x452dc8,0x43ee94,0x450b98,0x450bcc,0x440a18,0x440494,0x44dca2]
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in names)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_visible_area',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('hidden','screen','outside','simple','parent','parent_hidden','parent_outside'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   obj=0x2007f100;par=0x2007f200;area=0x2007f300;screen=0x2007f400;disp=0x2007f500
   u.mem_write(obj,b'\0'*64);u.mem_write(par,b'\0'*64);u.mem_write(obj+0x14,struct.pack('<4i',0,0,10,10));u.mem_write(par+0x14,struct.pack('<4i',0,0,8,8));u.mem_write(area,struct.pack('<4i',2,2,9,9));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,area)
   table={a:i for i,a in enumerate(native if not is_c else [sym[n]&~1 for n in names])};seen=[]
   def hook(uc,a,size,_):
    if a not in table:return
    k=table[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);seen.append((k,r0 if k in (0,1,2,8,12,14) else 0,r1 if k==0 else 0))
    if k==0:ret=1 if (mode=='hidden' and r0==obj and r1==1) or (mode=='parent_hidden' and r0==par and r1==1) else 0
    elif k==1:ret=screen
    elif k==2:ret=disp
    elif k in (3,4,5,6,7):ret=screen if (k==3 and mode!='screen') else 0
    elif k==8:ret=2
    elif k==9:uc.mem_write(r0,bytes(uc.mem_read(r1,16)));ret=0
    elif k==10:
     v=list(struct.unpack('<4i',bytes(uc.mem_read(r0,16))));v[0]-=r1;v[1]-=r2;v[2]+=r1;v[3]+=r2;uc.mem_write(r0,struct.pack('<4i',*v));ret=0
    elif k==11:
     if mode in ('outside','parent_outside') and (mode=='outside' or r2>=0x200ff000-100):ret=0
     else:uc.mem_write(r0,bytes(uc.mem_read(r1,16)));ret=1
    elif k==12:ret=0
    elif k==13:ret=0
    else:ret=par if mode.startswith('parent') and r0==obj else 0
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook);u.emu_start((sym['audio_uart_lv_visible_area'] if is_c else 0x4406c4)|1,0x600000,count=500)
   pair.append((u.reg_read(UC_ARM_REG_R0),seen,bytes(u.mem_read(area,16))))
  assert pair[0]==pair[1],(mode,pair)
  cases+=1
 print('PASS_DISPLAY_LV_VISIBLE_AREA_NATIVE',cases)
