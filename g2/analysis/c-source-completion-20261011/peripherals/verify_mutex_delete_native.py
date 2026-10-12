#!/usr/bin/env python3
"""Native/C CMSIS mutex deletion effects for stock 0x44986e."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/mutex_delete.c'
SHIM='''#include <stdint.h>
uint32_t audio_irq_context(void){return 0;}
int32_t audio_queue_delete(void*q){(void)q;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'shim.c').write_text(SHIM);elf=t/'m.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_mutex_delete',str(S),str(t/'shim.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(c,handle,irq):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  irq_addr=(sy['audio_irq_context']&~1) if c else 0x44900e
  del_addr=(sy['audio_queue_delete']&~1) if c else 0x441ea2
  calls=[]
  def hook(uc,addr,size,user):
   if addr==irq_addr:uc.reg_write(UC_ARM_REG_R0,irq)
   elif addr==del_addr:calls.append(uc.reg_read(UC_ARM_REG_R0));uc.reg_write(UC_ARM_REG_R0,0)
   else:return
   uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.reg_write(UC_ARM_REG_R0,handle);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['audio_uart_mutex_delete'] if c else 0x44986e)|1,0x600000,count=10000)
  return u.reg_read(UC_ARM_REG_R0),calls
 cases=0
 for irq in (0,1):
  for handle in (0,1,0x20050000,0x20050001):
   a=run(False,handle,irq);b=run(True,handle,irq)
   assert a==b,(irq,handle,a,b)
   cases+=1
 print('PASS_MUTEX_DELETE_NATIVE',cases)
