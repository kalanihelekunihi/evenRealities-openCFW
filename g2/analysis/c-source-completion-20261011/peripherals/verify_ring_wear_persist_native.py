#!/usr/bin/env python3
"""Bounded compiled-C/stock wear-persistence gateway effects."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_wear_persist.c'
STUB='''#include <stdint.h>
volatile uint8_t audio_uart_ring_persist_initialized,audio_uart_ring_persist_wake_pending,audio_uart_ring_persist_wake_blocked;
uint8_t audio_uart_ring_persist_queue_state[32];
void audio_uart_ring_persist_initialize_48eac8(void){}
void audio_uart_ring_persist_submit_48ea66(uint32_t a,uint32_t b,const void *p){(void)a;(void)b;(void)p;}
void audio_uart_ring_persist_notify_47dd92(void){}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_wear_persist_48eb32',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0,1,1,0,0,0),(1,12,1,0,0,0),(1,4,0,0,0,0),(1,4,1,0xc00,0,0),(1,4,1,0xc00,1,0),(1,4,1,0xc00,0,1)]
 for init,length,present,used,pending,blocked in cases:
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cells={'audio_uart_ring_persist_initialized':0x20075032,'audio_uart_ring_persist_wake_pending':0x20075037,'audio_uart_ring_persist_wake_blocked':0x20075036,'audio_uart_ring_persist_queue_state':0x200771f4}
   def cell(n):return sym[n] if is_c else cells[n]
   for n,v in [('audio_uart_ring_persist_initialized',init),('audio_uart_ring_persist_wake_pending',pending),('audio_uart_ring_persist_wake_blocked',blocked)]:u.mem_write(cell(n),bytes([v]))
   u.mem_write(cell('audio_uart_ring_persist_queue_state')+8,struct.pack('<I',used));u.mem_write(cell('audio_uart_ring_persist_queue_state')+16,struct.pack('<I',0))
   trace=[]
   hooks=[('audio_uart_ring_persist_initialize_48eac8',0x48eac8),('audio_uart_ring_persist_submit_48ea66',0x48ea66),('audio_uart_ring_persist_notify_47dd92',0x47dd92)]
   for n,a in hooks:
    addr=sym[n] if is_c else a
    def hook(uc,address,size,user_data,n=n):
     r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2)
     if n=='audio_uart_ring_persist_submit_48ea66':trace.append(('submit',r0,r1,r2))
     elif n=='audio_uart_ring_persist_initialize_48eac8':trace.append(('init',));uc.mem_write(cell('audio_uart_ring_persist_initialized'),b'\x01')
     else:trace.append(('notify',))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   p=0x2007f100;u.mem_write(p,b'ABCD')
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x60102);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_R2,p if present else 0)
   u.emu_start((sym['audio_uart_ring_wear_persist_48eb32'] if is_c else 0x48eb32)|1,0x600000,count=3000)
   pair.append((trace,u.mem_read(cell('audio_uart_ring_persist_wake_pending'),1)[0]))
  assert pair[0]==pair[1],(init,length,present,used,pending,blocked,pair)
 print('PASS_RING_WEAR_PERSIST_NATIVE',len(cases))
