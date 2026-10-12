#!/usr/bin/env python3
"""Stock/C ring manager queue/create/terminate successful-state effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_task_producer.c'
STUB='''#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
struct ring_thread_manager audio_uart_ring_thread_manager;
uint8_t audio_uart_ring_thread_cb[112],audio_uart_ring_thread_stack[4096];
void thread_ring_entry(void *p){(void)p;}
void *audio_queue_new(uint32_t a,uint32_t b,const void *c){(void)a;(void)b;(void)c;return 0;}
void *audio_thread_new(void (*f)(void *),void *a,const void *b){(void)f;(void)a;(void)b;return 0;}
int32_t audio_thread_terminate_peer(void *p){(void)p;return 0;}
uint32_t audio_wsf_interrupt_mask_set(void){return 0;}
'''
def w(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,thread_ring_create',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for name,addr in [('thread_ring_queue_init',0x4c4d66),('thread_ring_create',0x4c4da4),('thread_ring_terminate',0x4c4dd0)]:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000);u.mem_map(0x20300000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cell=sym['audio_uart_ring_thread_manager'] if is_c else 0x20004120
   u.mem_write(cell,b'\0'*16);u.mem_write(cell+8,struct.pack('<I',0x2007f100))
   trace=[]
   hooks=[('audio_queue_new',0x449a32),('audio_thread_new',0x4490e2),('audio_thread_terminate_peer',0x4491fe)]
   for h,native in hooks:
    target=sym[h] if is_c else native
    def hook(uc,address,size,data,h=h):
     a,b,c=[uc.reg_read(q) for q in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2)]
     if h=='audio_queue_new':trace.append((h,a,b,c));uc.reg_write(UC_ARM_REG_R0,0x2007f300)
     elif h=='audio_thread_new':
      fields=[w(uc,c+i) for i in range(0,36,4)]
      task=bytes(uc.mem_read(fields[0],16)).split(b'\0')[0]
      trace.append((h,b,task,fields[1],fields[3],fields[5:]))
      uc.reg_write(UC_ARM_REG_R0,0x2007f200)
     else:trace.append((h,a));uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym[name] if is_c else addr)|1,0x600000,count=2000)
   pair.append((trace,w(u,cell+8),w(u,cell+12)))
  assert pair[0]==pair[1],(name,pair)
 print('PASS_RING_TASK_PRODUCER_NATIVE',3)
