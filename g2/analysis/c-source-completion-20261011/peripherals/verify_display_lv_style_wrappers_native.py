#!/usr/bin/env python3
"""Native/C LV style wrapper, dispatcher and page clear effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
S=[D/x for x in ('display_lv_page_style_wrappers.c','display_lv_page_style_apply.c','display_page_manager_clear.c')]
stub='''#include <stdint.h>
__attribute__((naked)) uint32_t audio_uart_page_style_selector_44b860(uint32_t a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_page_style_resolve_44ca18(void*a,uint32_t b,uint8_t c,uint32_t d){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_page_style_local_44c5d4(void*a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) uint32_t audio_uart_page_style_needs_invalidate_44b844(uint8_t a,uint32_t b){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_display_size_changed(void*a){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_page_style_value_482868(uint32_t a,uint8_t b,uint32_t c){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_page_style_refresh_44bc8c(void*a,uint32_t b,uint8_t c){__asm volatile("bx lr");}
__attribute__((naked)) void audio_uart_buffer_zero(void*a,uint32_t b,uint32_t c){__asm volatile("bx lr");}
'''
names=['44120e','44121c','44122a','441238','44129e','44131c','44133a','441378','441386','441394','4413a2','4413b0','44146a','45ec7c','45fb7c','45fba2']
lower={'audio_uart_page_style_selector_44b860':0x44b860,'audio_uart_page_style_resolve_44ca18':0x44ca18,
       'audio_uart_page_style_local_44c5d4':0x44c5d4,'audio_uart_page_style_needs_invalidate_44b844':0x44b844,
       'audio_uart_display_size_changed':0x440656,'audio_uart_page_style_value_482868':0x482868,
       'audio_uart_page_style_refresh_44bc8c':0x44bc8c,'audio_uart_buffer_zero':0x43c0e4}
with tempfile.TemporaryDirectory() as td:
 mock=Path(td)/'mock.c';mock.write_text(stub);elf=Path(td)/'candidate.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_page_45ec7c',*[str(x) for x in S],str(mock),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  x=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in x.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in x.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for name in names:
  for selector in (0,1):
   for valid in ((False,True) if name in ('45fb7c','45fba2') else (True,)):
    pair=[]
    for is_c in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     obj=0x2007f100;u.mem_write(obj,bytes([0x7a]*0x200));u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
     u.reg_write(UC_ARM_REG_R0,obj if valid else 0);u.reg_write(UC_ARM_REG_R1,0x12345678);u.reg_write(UC_ARM_REG_R2,selector)
     seen=[];reverse={v:k for k,v in lower.items()};reverse_c={sym[k]&~1:k for k in lower}
     def hook(uc,a,size,_):
      k=(reverse_c if is_c else reverse).get(a)
      if not k:return
      arity={'audio_uart_page_style_selector_44b860':1,'audio_uart_page_style_local_44c5d4':2,
             'audio_uart_page_style_needs_invalidate_44b844':2,'audio_uart_display_size_changed':1}.get(k,3)
      seen.append((k,*[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)[:arity]]))
      if k=='audio_uart_buffer_zero':
       p=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);uc.mem_write(p,bytes([0]*n))
      uc.reg_write(UC_ARM_REG_R0,1 if k=='audio_uart_page_style_needs_invalidate_44b844' else 0x2007f300)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook)
     entry=sym['audio_uart_page_'+name] if is_c else int(name,16)
     u.emu_start(entry|1,0x600000,count=500)
     pair.append((seen,bytes(u.mem_read(obj,0x100)) if name in ('45fb7c','45fba2') else None))
    assert pair[0]==pair[1],(name,selector,valid,pair)
    cases+=1
 print('PASS_DISPLAY_LV_STYLE_WRAPPERS_NATIVE',cases)
