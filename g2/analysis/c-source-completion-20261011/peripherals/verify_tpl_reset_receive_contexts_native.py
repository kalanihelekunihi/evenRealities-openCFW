#!/usr/bin/env python3
"""Actual compiled-C/native reset loop call-order oracle for all 16 row masks."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_tpl_reset_receive_contexts.c'
STUB='''#include <stdint.h>
uint8_t audio_tpl_contexts[224];
void audio_tpl_rx_next_packet_timeout(void){}
uint32_t audio_event_loop_remove_delayed(void(*p)(void)){(void)p;return 0;}
void tpl_context_free_004b8ba2(uint8_t*p){(void)p;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,tpl_reset_receive_contexts_004b9984',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,mask):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  base=sy['audio_tpl_contexts'] if compiled else 0x20070dc8
  rows=bytearray(224)
  for i in range(4):rows[56*i+0x30]=(mask>>i)&1
  u.mem_write(base,bytes(rows));trace=[]
  names=[('remove','audio_event_loop_remove_delayed',0x476ace),('free','tpl_context_free_004b8ba2',0x4b8ba2)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0=uc.reg_read(UC_ARM_REG_R0)
    if name=='remove':trace.append(('remove',r0==((sy['audio_tpl_rx_next_packet_timeout']&~1)|1) if compiled else r0==0x4b8c6d))
    else:trace.append(('free',(r0-base)//56,r0>=base and r0<base+224))
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['tpl_reset_receive_contexts_004b9984'] if compiled else 0x4b9984)|1,0x600000,count=3000)
  return trace
 for mask in range(16):
  a,b=run(False,mask),run(True,mask)
  assert a==b,(mask,a,b)
 print('PASS_TPL_RESET_CONTEXTS_NATIVE',16)
