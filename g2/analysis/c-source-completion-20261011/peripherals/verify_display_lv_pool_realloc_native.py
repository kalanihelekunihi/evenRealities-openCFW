#!/usr/bin/env python3
"""Actual ARM/C LV pool realloc accounting and lock effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_lv_realloc.c'
funcs=['xQueueSemaphoreTake','audio_uart_queue_send','g2_tlsf_reallocate_4d0868','g2_tlsf_block_size','audio_uart_lv_heap_free','audio_uart_lv_malloc','audio_uart_lvgl_log']
stub='#include <stdint.h>\n'+''.join('__attribute__((naked)) uint32_t '+n+'(){__asm volatile("bx lr");}\n' for n in funcs)
with tempfile.TemporaryDirectory() as td:
 m=Path(td)/'m.c';m.write_text(stub);elf=Path(td)/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,--defsym,audio_uart_lv_heap_pool=0x20000338','-Wl,--defsym,audio_uart_lv_static_slot=0x2006f5ac','-Wl,-e,audio_uart_lv_pool_realloc_484234',str(S),str(m),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 cases=0
 for taken in (False,True):
  for success in (False,True):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    cell=0x2007f100;old=0x2007f300;new=0x2007f400;mutex=0x2007f500;tlsf=0x2007f600
    u.mem_write(cell,struct.pack('<IIII',mutex,tlsf,100,120))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,cell);u.reg_write(UC_ARM_REG_R1,old);u.reg_write(UC_ARM_REG_R2,80)
    seen=[];mapn={0x441c44:'lock',0x4d05e4:'size',0x4d0868:'realloc',0x4417ee:'unlock'} if not is_c else {sym['xQueueSemaphoreTake']&~1:'lock',sym['g2_tlsf_block_size']&~1:'size',sym['g2_tlsf_reallocate_4d0868']&~1:'realloc',sym['audio_uart_queue_send']&~1:'unlock'}
    def hook(uc,a,size,_):
     if a in mapn:
      k=mapn[a];r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
      if k=='size':r0+=8 if is_c else 0
      seen.append((k,r0,r1 if k in ('lock','realloc') else 0,r2 if k=='realloc' else 0))
      val=int(taken) if k=='lock' else (12 if r0==old else 20) if k=='size' else new if k=='realloc' and success else 0
      uc.reg_write(UC_ARM_REG_R0,val);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start((sym['audio_uart_lv_pool_realloc_484234'] if is_c else 0x484234)|1,0x600000,count=200)
    pair.append((seen,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(cell,16))))
   assert pair[0]==pair[1],(taken,success,pair)
   cases+=1
 print('PASS_DISPLAY_LV_POOL_REALLOC_NATIVE',cases)
