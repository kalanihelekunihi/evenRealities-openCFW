#!/usr/bin/env python3
"""Actual ARM/C transition-list unlink, node release and schedule effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate';S=[D/'display_lv_style_transition_unlink.c',D/'display_lv_style_list.c']
stub='''#include <stdint.h>
void *audio_uart_lv_list_first(void*l){return *(void**)((uint8_t*)l+4);}
void *audio_uart_lv_list_next(void*l,void*n){return *(void**)((uint8_t*)n+*(uint32_t*)l+4);}
__attribute__((naked)) void audio_uart_lv_heap_free(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_transition_schedule_4509da(void){__asm volatile("bx lr");}
'''
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_display_lv_root=0x2006f548','-Wl,-e,audio_uart_lv_style_unlink_450500',*[str(x) for x in S],str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for match in (False,True):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   li=0x2006f5f4;n1=0x2007f200;n2=0x2007f300;obj=0x2007f500;style=0x2007f600
   u.mem_write(li,struct.pack('<III',0x18,n1,n2))
   u.mem_write(n1,struct.pack('<II',obj,style)+b'\0'*0x10+struct.pack('<II',0,n2))
   u.mem_write(n2,struct.pack('<II',obj+4,style)+b'\0'*0x10+struct.pack('<II',n1,0))
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,obj if match else 0x2007f900);u.reg_write(UC_ARM_REG_R1,style)
   seen=[]
   def hook(uc,a,size,_):
    if a in (0x44f758,sym['audio_uart_lv_heap_free']&~1):seen.append(('free',uc.reg_read(UC_ARM_REG_R0)));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
    if a in (0x4509da,sym['audio_uart_lv_transition_schedule_4509da']&~1):seen.append(('schedule',));uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_style_unlink_450500'] if is_c else 0x450500)|1,0x600000,count=300)
   pair.append((seen,u.reg_read(UC_ARM_REG_R0)&0xff,bytes(u.mem_read(li,12)),bytes(u.mem_read(n1+0x18,8)),bytes(u.mem_read(n2+0x18,8))))
  assert pair[0]==pair[1],(match,pair)
 print('PASS_DISPLAY_LV_STYLE_TRANSITION_UNLINK_NATIVE',2)
