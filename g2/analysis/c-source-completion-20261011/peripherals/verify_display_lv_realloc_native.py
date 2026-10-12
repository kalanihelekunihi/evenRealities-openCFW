#!/usr/bin/env python3
"""Actual ARM/C LV realloc front-end size-zero, static-slot and pool paths."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_realloc.c'
funcs=['xQueueSemaphoreTake','audio_uart_queue_send','g2_tlsf_reallocate_4d0868','g2_tlsf_block_size','audio_uart_lv_heap_free','audio_uart_lv_malloc','audio_uart_lvgl_log']
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in funcs)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_lv_heap_pool=0x20000338','-Wl,--defsym,audio_uart_lv_static_slot=0x2006f5ac','-Wl,-e,audio_uart_lv_realloc_44f76a',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for mode in ('zero','static','pool_ok','pool_fail'):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   ptr=0x2006f5ac if mode=='static' else 0x2007f100
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,ptr);u.reg_write(UC_ARM_REG_R1,0 if mode=='zero' else 24)
   seen=[];maps={0x44f758:'free',0x44f718:'malloc',0x48432a:'pool',0x44d25c:'log'} if not is_c else {sym['audio_uart_lv_heap_free']&~1:'free',sym['audio_uart_lv_malloc']&~1:'malloc',sym['audio_uart_lv_pool_realloc_48432a']&~1:'pool',sym['audio_uart_lvgl_log']&~1:'log'}
   def hook(uc,a,size,_):
    if a in maps:
     k=maps[a];seen.append((k,uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1) if k=='pool' else 0))
     if k=='malloc':uc.reg_write(UC_ARM_REG_R0,0x2007f500)
     if k=='pool':uc.reg_write(UC_ARM_REG_R0,0 if mode=='pool_fail' else 0x2007f600)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook)
   u.emu_start((sym['audio_uart_lv_realloc_44f76a'] if is_c else 0x44f76a)|1,0x600000,count=100)
   pair.append((seen,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(mode,pair)
  cases+=1
 print('PASS_DISPLAY_LV_REALLOC_NATIVE',cases)
