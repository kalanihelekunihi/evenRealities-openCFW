#!/usr/bin/env python3
"""Compare stock and actual ARM C event queue routing on defined inputs."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_persist_event_operation.c'
Q=R/'components/audio/timer_drain_full_source_candidate/queue_state.c'
STUB='''#include <stdint.h>
uint32_t audio_scheduler_state(void){return 0;} uint32_t audio_wsf_interrupt_mask_set(void){return 0;}
int32_t xQueueGenericSend(void*q,const void*p,uint32_t t,int32_t w){(void)q;(void)p;(void)t;(void)w;return 0;}
int32_t xQueueGenericSendFromISR(void*q,const void*p,int32_t*t,int32_t w){(void)q;(void)p;(void)t;(void)w;return 0;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_persist_wait_event_47e7b0',str(S),str(Q),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for queue in (0,0x20070000):
  for priority in (4,6,0xffffffff):
   for scheduler in (1,2):
    pair=[]
    for compiled in (False,True):
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
     u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
     for a,d in seg:u.mem_write(a,d)
     u.mem_write(sym['audio_uart_ring_persist_queue_handle_20074ab0'] if compiled else 0x20074ab0,struct.pack('<I',queue))
     trace=[]
     for name,cs,stock in (('scheduler','audio_scheduler_state',0x4558a4),('send','xQueueGenericSend',0x4417ee),('isr','xQueueGenericSendFromISR',0x441952)):
      target=sym[cs] if compiled else stock
      def hook(uc,pc,size,user,name=name):
       if name=='scheduler':uc.reg_write(UC_ARM_REG_R0,scheduler)
       else:
        p=uc.reg_read(UC_ARM_REG_R1)
        trace.append((name,uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(p,12)),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3)))
        uc.reg_write(UC_ARM_REG_R0,1)
       uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
      u.hook_add(UC_HOOK_CODE,hook,begin=target&~1,end=target&~1)
     u.reg_write(UC_ARM_REG_R0,0x1234);u.reg_write(UC_ARM_REG_R1,priority);u.reg_write(UC_ARM_REG_R2,0x5678);u.reg_write(UC_ARM_REG_R3,0)
     u.reg_write(UC_ARM_REG_SP,0x200ff000);u.mem_write(0x200ff000,struct.pack('<I',99));u.reg_write(UC_ARM_REG_LR,0x600001)
     u.emu_start((sym['audio_uart_ring_persist_wait_event_47e7b0'] if compiled else 0x47e7b0)|1,0x600000,count=1000)
     pair.append((u.reg_read(UC_ARM_REG_R0),trace))
    assert pair[0]==pair[1],(queue,priority,scheduler,pair)
print('PASS_RING_PERSIST_EVENT_OPERATION_NATIVE 12')
