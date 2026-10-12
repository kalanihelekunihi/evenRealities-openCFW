#!/usr/bin/env python3
"""Native/C LV list resolver, selector and invalidate-flag branches."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_style_resolve.c'
stub='''#include <stdint.h>
uint8_t audio_uart_display_lv_root[0x40];
__attribute__((naked)) void *audio_uart_lv_list_first_482ce4(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void *audio_uart_lv_list_next_482cfa(void*a,void*b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_style_notify_4827b0(void*a,int8_t b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_style_unlink_450500(void*a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_list_remove_482c0e(void*a,void*b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_lv_style_release_44f758(void*a){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_lv_property_flags_482a6a(uint8_t a){__asm volatile("bx lr");}
'''
native={'audio_uart_lv_list_first_482ce4':0x482ce4,'audio_uart_lv_list_next_482cfa':0x482cfa,
        'audio_uart_lv_style_notify_4827b0':0x4827b0,'audio_uart_lv_style_unlink_450500':0x450500,
        'audio_uart_lv_list_remove_482c0e':0x482c0e,'audio_uart_lv_style_release_44f758':0x44f758,
        'audio_uart_lv_property_flags_482a6a':0x482a6a}
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_page_style_resolve_44ca18',str(S),str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('resolve','selector','flag'):
  params=[(g,p,s) for g in (0x10000,0xf0000,0x20000) for p in (0x30,0x31,0xff) for s in (0,1)] if mode=='resolve' else [(x,0,0) for x in (0,1,0x12345678,0xffffffff)]
  for group,prop,stop in params:
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    root=(sym['audio_uart_display_lv_root']+0x18) if is_c else 0x2006f560
    obj=0x2007f100;node=0x2007f300;table=0x2007f500
    u.mem_write(obj,bytes([0]*0x100));u.mem_write(node,struct.pack('<III',obj,0x30,0x10000));u.mem_write(obj+0xc,struct.pack('<I',table));u.mem_write(obj+0x2a,struct.pack('<H',16))
    u.mem_write(table,struct.pack('<II',0x2007f600,0x02010000))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    if mode=='resolve':
     u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_R1,group);u.reg_write(UC_ARM_REG_R2,prop);u.reg_write(UC_ARM_REG_R3,node if stop else 0)
    else:u.reg_write(UC_ARM_REG_R0,group);u.reg_write(UC_ARM_REG_R1,0x20)
    seen=[];reverse={v:k for k,v in native.items()};reverse_c={sym[k]&~1:k for k in native}
    def hook(uc,a,size,_):
     k=(reverse_c if is_c else reverse).get(a)
     if not k:return
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
     if r0==root:r0='root'
     arity=1 if k in ('audio_uart_lv_list_first_482ce4','audio_uart_lv_style_release_44f758','audio_uart_lv_property_flags_482a6a') else 2
     seen.append((k,r0,r1) if arity==2 else (k,r0))
     if k=='audio_uart_lv_list_first_482ce4':rv=node
     elif k=='audio_uart_lv_list_next_482cfa':rv=0
     elif k=='audio_uart_lv_property_flags_482a6a':rv=0x20
     else:rv=0
     uc.reg_write(UC_ARM_REG_R0,rv);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    entry=sym[{'resolve':'audio_uart_page_style_resolve_44ca18','selector':'audio_uart_page_style_selector_44b860','flag':'audio_uart_page_style_needs_invalidate_44b844'}[mode]] if is_c else {'resolve':0x44ca18,'selector':0x44b860,'flag':0x44b844}[mode]
    u.emu_start(entry|1,0x600000,count=500)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(mode,group,prop,stop,pair)
   cases+=1
 print('PASS_DISPLAY_LV_STYLE_RESOLVE_NATIVE',cases)
