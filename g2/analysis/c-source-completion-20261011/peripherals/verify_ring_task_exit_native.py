#!/usr/bin/env python3
"""Stock/C ring exit queue release, synchronization, first delay effect."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_task_exit.c'
STUB='''#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
struct ring_thread_manager audio_uart_ring_thread_manager;
void audio_uart_ring_sync_exit_4c9c3c(uint32_t x){(void)x;}
int32_t audio_queue_delete_peer(void *p){(void)p;return 0;}
void audio_delay(uint32_t x){(void)x;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
def w(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_exit_4c53a6',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for present in (False,True):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cell=sym['audio_uart_ring_thread_manager'] if is_c else 0x20004120
   u.mem_write(cell+12,struct.pack('<I',0x2007f100 if present else 0))
   trace=[]
   hooks=[('audio_uart_ring_sync_exit_4c9c3c',0x4c9c3c),('audio_queue_delete_peer',0x449bec),('audio_log_flags',0x43d0ce),('audio_delay',0x449376)]
   for n,a in hooks:
    addr=sym[n] if is_c else a
    def hook(uc,address,size,data,n=n):
     r0=uc.reg_read(UC_ARM_REG_R0);trace.append((n,r0) if n!='audio_log_flags' else (n,))
     if n=='audio_delay':uc.emu_stop();return
     if n=='audio_log_flags':uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_exit_4c53a6'] if is_c else 0x4c53a6)|1,0,count=3000)
   pair.append((trace,w(u,cell+12)))
  assert pair[0]==pair[1],(present,pair)
 print('PASS_RING_TASK_EXIT_NATIVE',2)
