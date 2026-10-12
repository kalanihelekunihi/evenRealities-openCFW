#!/usr/bin/env python3
"""Actual compiled-C/native TPL context free call and memory effects."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_tpl_context_free.c'
STUB='''#include <stdint.h>
uint32_t audio_event_loop_remove_delayed(void(*p)(void)){(void)p;return 0;}
void audio_tpl_rx_next_packet_timeout(void){}
void audio_file_heap_free(void*p){(void)p;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);(t/'stub.c').write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding','-fno-builtin','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,tpl_context_free_004b8ba2',str(S),str(t/'stub.c'),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sy={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 def run(compiled,present,used,allocated):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
  u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
  for a,d in seg:u.mem_write(a,d)
  row=0x20081000;buf=0x20082000;d=bytearray([0xa5]*56);d[0x30]=used;d[8:12]=struct.pack('<I',buf if allocated else 0);u.mem_write(row,bytes(d));trace=[]
  names=[('remove','audio_event_loop_remove_delayed',0x476ace),('free','audio_file_heap_free',0x474d16),('zero','audio_uart_buffer_zero',0x43c0e4)]
  for name,cs,ns in names:
   a=(sy[cs]&~1) if compiled else ns
   def hook(uc,pc,n,user,name=name):
    r0,r1,r2=[uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
    if name=='remove':trace.append(('remove',r0==((sy['audio_tpl_rx_next_packet_timeout']&~1)|1) if compiled else r0==0x4b8c6d))
    elif name=='free':trace.append(('free',r0==buf))
    else:trace.append(('zero',r0==row,r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
    uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a)
  u.reg_write(UC_ARM_REG_R0,row if present else 0);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
  u.emu_start((sy['tpl_context_free_004b8ba2'] if compiled else 0x4b8ba2)|1,0x600000,count=1000)
  return bytes(u.mem_read(row,56)),trace
 cases=0
 for present in (0,1):
  for used in (0,1):
   for allocated in (0,1):
    a,b=run(False,present,used,allocated),run(True,present,used,allocated)
    assert a==b,(present,used,allocated,a,b)
    cases+=1
 print('PASS_TPL_CONTEXT_FREE_NATIVE',cases)
