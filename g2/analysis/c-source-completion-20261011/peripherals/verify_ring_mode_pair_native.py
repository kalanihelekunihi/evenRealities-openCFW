#!/usr/bin/env python3
"""Stock/compiled-C low-mode forwarding and pair packet bytes."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=R/'components/audio/uart_thread_source_candidate'
STUB='''#include <stdint.h>
int32_t audio_uart_ring_task_msg_send(uint32_t a,const void *b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
void audio_uart_buffer_zero(void *a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;}
uint32_t audio_uart_ring_ble_send_data_4c4b7e(const void *a,uint32_t b){(void)a;(void)b;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_mode_update_472362',str(SRC/'display_ring_mode_update.c'),str(SRC/'display_ring_pair_mode.c'),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for kind in ('mode','pair'):
  for value in ((0,0x1357,0xfedc) if kind=='mode' else (0,)):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    trace=[]
    hooks=[('audio_uart_ring_task_msg_send',0x4c549c),('audio_uart_buffer_zero',0x43c0e4),('audio_uart_ring_ble_send_data_4c4b7e',0x4c4b7e)]
    for n,a in hooks:
     addr=sym[n] if is_c else a
     def hook(uc,address,size,user_data,n=n):
      r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
      if n=='audio_uart_ring_task_msg_send':trace.append(('task_send',r0,r2,bytes(uc.mem_read(r1,2))));uc.reg_write(UC_ARM_REG_R0,0)
      elif n=='audio_uart_buffer_zero':trace.append(('zero',r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
      else:trace.append(('ble_send',r1,bytes(uc.mem_read(r0,r1))));uc.reg_write(UC_ARM_REG_R0,0)
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,value)
    name,stock=(('audio_uart_ring_mode_update_472362',0x472362) if kind=='mode' else ('audio_uart_ring_pair_mode_472546',0x472546))
    u.emu_start((sym[name] if is_c else stock)|1,0x600000,count=3000)
    pair.append((trace,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(kind,value,pair)
 print('PASS_RING_MODE_PAIR_NATIVE',4)
