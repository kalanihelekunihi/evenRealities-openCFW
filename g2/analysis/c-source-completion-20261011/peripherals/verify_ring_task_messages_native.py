#!/usr/bin/env python3
"""Stock/C ring queue dispatch and ownership for each native message ID."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_task_messages.c'
STUB='''#include <stdint.h>
struct ring_thread_manager {uint8_t reserved[8];void *thread;void *queue;};
struct ring_thread_manager audio_uart_ring_thread_manager;
int32_t audio_uart_queue_receive(void *a,void *b,uint32_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
void audio_file_heap_free(void *p){(void)p;}
void audio_uart_ring_send_packet_472988(const void *p,uint32_t n){(void)p;(void)n;}
void audio_uart_ring_message_80_472378(uint8_t x){(void)x;}
void audio_uart_ring_message_400_4723d6(uint8_t x,uint8_t y){(void)x;(void)y;}
void audio_uart_ring_message_1000_4722d8(uint16_t x){(void)x;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
def w(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_msg_handler_4c4de8',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 children=[('audio_uart_queue_receive',0x449b3c),('audio_file_heap_free',0x474d16),('audio_uart_ring_send_packet_472988',0x472988),('audio_uart_ring_message_80_472378',0x472378),('audio_uart_ring_message_400_4723d6',0x4723d6),('audio_uart_ring_message_1000_4722d8',0x4722d8),('audio_log_flags',0x43d0ce)]
 cases=[(2,2),(0x80,1),(0x400,1),(0x1000,2),(0x1000,1),(0x777,2)]
 for id,length in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cell=sym['audio_uart_ring_thread_manager'] if is_c else 0x20004120
   msg=0x2007f100;u.mem_write(cell+12,struct.pack('<I',0x2007f000));u.mem_write(msg,struct.pack('<II',id,length)+b'\x12\x34\x56\x78')
   trace=[];reads=[0]
   for name,native in children:
    addr=sym[name] if is_c else native
    def hook(uc,address,size,data,name=name):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
     if name=='audio_uart_queue_receive':
      trace.append(('get',r0,uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
      if reads[0]==0:uc.mem_write(r1,struct.pack('<I',msg));uc.reg_write(UC_ARM_REG_R0,0)
      else:uc.reg_write(UC_ARM_REG_R0,1)
      reads[0]+=1
     elif name=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,0)
     elif name=='audio_file_heap_free':trace.append(('free',r0))
     elif name=='audio_uart_ring_send_packet_472988':trace.append(('packet',r0,r1))
     elif name=='audio_uart_ring_message_400_4723d6':trace.append(('400',r0,r1))
     else:trace.append((name,r0))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_msg_handler_4c4de8'] if is_c else 0x4c4de8)|1,0x600000,count=4000)
   pair.append(trace)
  assert pair[0]==pair[1],(id,length,pair)
 print('PASS_RING_TASK_MESSAGES_NATIVE',len(cases))
