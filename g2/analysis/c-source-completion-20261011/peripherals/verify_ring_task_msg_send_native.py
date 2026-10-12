#!/usr/bin/env python3
"""Actual compiled-C/stock ring_task_msg_send allocation and dispatch."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_task_msg_send.c'
STUB='''#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
struct ring_thread_manager audio_uart_ring_thread_manager;
void *file_heap_allocate(uint32_t x){(void)x;return 0;}
void audio_file_heap_free(void *p){(void)p;}
void audio_uart_buffer_zero(void *p,uint32_t n,uint32_t v){(void)p;(void)n;(void)v;}
void *audio_queue_copy_bytes(void *p,const void *q,uint32_t n){(void)q;(void)n;return p;}
int32_t audio_cmsis_queue_put(void *q,const void *p,uint8_t priority,uint32_t ticks){(void)q;(void)p;(void)priority;(void)ticks;return 0;}
uint32_t audio_thread_flags_set(void *t,uint32_t f){(void)t;return f;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_task_msg_send',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for scenario in ('null','queue_missing','alloc_fail','put_fail','success'):
  for level in (0,7):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    mgr=sym['audio_uart_ring_thread_manager'] if is_c else 0x20004120
    queue=0 if scenario=='queue_missing' else 0x2007f300;thread=0x2007f400;node=0x2007f100;data=0x2007f200
    u.mem_write(mgr+8,struct.pack('<II',thread,queue));u.mem_write(node,b'\xaa'*16);u.mem_write(data,b'xyz123')
    trace=[]
    hooks=[('file_heap_allocate',0x474cd2),('audio_file_heap_free',0x474d16),('audio_uart_buffer_zero',0x43c0e4),('audio_queue_copy_bytes',0x439be4),('audio_cmsis_queue_put',0x449abe),('audio_thread_flags_set',0x449238),('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
    for n,a in hooks:
     addr=sym[n] if is_c else a
     def hook(uc,address,size,user_data,n=n):
      r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
      if n=='file_heap_allocate':trace.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,0 if scenario=='alloc_fail' else node)
      elif n=='audio_file_heap_free':trace.append(('free',r0))
      elif n=='audio_uart_buffer_zero':trace.append(('zero',r0,r1,r2));uc.mem_write(r0,bytes([r2&255])*r1)
      elif n=='audio_queue_copy_bytes':trace.append(('copy',r0,r1,r2));uc.mem_write(r0,bytes(uc.mem_read(r1,r2)));uc.reg_write(UC_ARM_REG_R0,r0)
      elif n=='audio_cmsis_queue_put':
       p=int.from_bytes(uc.mem_read(r1,4),'little');trace.append(('put',r0,p,bytes(uc.mem_read(p,11))));uc.reg_write(UC_ARM_REG_R0,1 if scenario=='put_fail' else 0)
      elif n=='audio_thread_flags_set':trace.append(('flags_set',r0,r1));uc.reg_write(UC_ARM_REG_R0,r1)
      elif n=='audio_log_flags':trace.append(('log_flags',));uc.reg_write(UC_ARM_REG_R0,level)
      elif n=='audio_log_extended':trace.append(('extended',r0))
      else:trace.append(('compressed',r0))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,2);u.reg_write(UC_ARM_REG_R1,0 if scenario=='null' else data);u.reg_write(UC_ARM_REG_R2,3)
    u.emu_start((sym['audio_uart_ring_task_msg_send'] if is_c else 0x4c549c)|1,0x600000,count=3000)
    pair.append((trace,struct.unpack('<i',struct.pack('<I',u.reg_read(UC_ARM_REG_R0)))[0],bytes(u.mem_read(node,11))))
   assert pair[0]==pair[1],(scenario,level,pair)
 print('PASS_RING_TASK_MSG_SEND_NATIVE',10)
