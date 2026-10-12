#!/usr/bin/env python3
"""Bounded compiled ARM C/native SendDataToBoth queue and ownership effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_input_event_send.c'
STUB='''#include <stdint.h>
void *audio_uart_input_queue;void *audio_uart_input_event_flags;
void *audio_uart_alloc_retry(uint32_t n){(void)n;return 0;}
void audio_file_heap_free(void*p){(void)p;}
void audio_uart_buffer_zero(void*p,uint32_t n,uint32_t x){(void)p;(void)n;(void)x;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t n){(void)b;(void)n;return a;}
int32_t audio_cmsis_queue_put(void*a,const void*b,uint8_t c,uint32_t d){(void)a;(void)b;(void)c;(void)d;return 0;}
uint32_t osEventFlagsSet(void*a,uint32_t b){(void)a;(void)b;return 0;}
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_input_event_send_464d1c',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for queue_present,alloc_fail,put_result in ((False,0,0),(True,1,0),(True,2,0),(True,0,0),(True,0,1)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   queue=sym['audio_uart_input_queue'] if is_c else 0x200749cc
   flags=sym['audio_uart_input_event_flags'] if is_c else 0x20074b10
   u.mem_write(queue,(0x20070000 if queue_present else 0).to_bytes(4,'little'))
   u.mem_write(flags,(0x20070004).to_bytes(4,'little'))
   payload=0x20090000;u.mem_write(payload,b'\x11\x22\x33\x44')
   trace=[]; allocations=[0x20080000,0x20080100];state=[0]
   hooks=[('alloc','audio_uart_alloc_retry',0x4646f0),('free','audio_file_heap_free',0x474d16),('zero','audio_uart_buffer_zero',0x43c0e4),('copy','audio_queue_copy_bytes',0x439be4),('put','audio_cmsis_queue_put',0x449abe),('set','osEventFlagsSet',0x4495e4),('flags','audio_log_level',0x43d0ce)]
   for name,symbol,native in hooks:
    addr=sym[symbol] if is_c else native
    def hook(uc,pc,size,user,name=name):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     if name=='alloc':
      state[0]+=1;trace.append(('alloc',r0));uc.reg_write(UC_ARM_REG_R0,0 if state[0]==alloc_fail else allocations[state[0]-1])
     elif name=='free':trace.append(('free',r0))
     elif name=='zero':uc.mem_write(r0,bytes([r2&255])*r1)
     elif name=='copy':uc.mem_write(r0,bytes(uc.mem_read(r1,r2)))
     elif name=='put':
      node=int.from_bytes(uc.mem_read(r1,4),'little')
      packet=int.from_bytes(uc.mem_read(node+8,4),'little')
      trace.append(('put',r0,r2,uc.reg_read(UC_ARM_REG_R3),bytes(uc.mem_read(node,8)),bytes(uc.mem_read(packet,12))))
      uc.reg_write(UC_ARM_REG_R0,put_result)
     elif name=='set':trace.append(('set',r0,r1));uc.reg_write(UC_ARM_REG_R0,r1)
     else:uc.reg_write(UC_ARM_REG_R0,0)
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x108);u.reg_write(UC_ARM_REG_R1,payload);u.reg_write(UC_ARM_REG_R2,4);u.reg_write(UC_ARM_REG_R3,0x1234)
   u.emu_start((sym['audio_uart_input_event_send_464d1c'] if is_c else 0x464d1c)|1,0x600000,count=5000)
   pair.append((u.reg_read(UC_ARM_REG_R0),trace))
  assert pair[0]==pair[1],((queue_present,alloc_fail,put_result),pair)
print('PASS_RING_INPUT_EVENT_NATIVE 5')
