#!/usr/bin/env python3
"""Compare stock and compiled ARM C persistence record append and eviction."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
D=R/'components/audio/uart_thread_source_candidate'
S=[D/'display_ring_persist_append.c',D/'display_ring_persist_buffer.c']
STUB='''#include <stdint.h>
uint8_t audio_uart_ring_persist_storage[4096];
uint8_t audio_uart_ring_persist_queue_state[24];
'''
def put(u,a,v):u.mem_write(a,int(v).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_persist_append_48e9be',*[str(s) for s in S],str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for read,write,tail,header in ((0,0,0,0),(0,4092,0,0xa2),(4092,4092,4092,0)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   q=sym['audio_uart_ring_persist_queue_state'] if is_c else 0x200771f4
   ring=sym['audio_uart_ring_persist_storage'] if is_c else 0x200761f4
   for off,val in ((0,0x31435054),(4,0x1000),(8,write),(12,read),(16,tail),(20,0)):put(u,q+off,val)
   put(u,ring,header)
   payload=0x20090000;put(u,payload,0x12345678);put(u,payload+4,0x9abcdef0)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x60102);u.reg_write(UC_ARM_REG_R1,2);u.reg_write(UC_ARM_REG_R2,payload);u.reg_write(UC_ARM_REG_R3,0x55667788)
   u.emu_start((sym['audio_uart_ring_persist_append_48e9be'] if is_c else 0x48e9be)|1,0x600000,count=10000)
   pair.append((bytes(u.mem_read(q,24)),bytes(u.mem_read(ring,4096))))
  assert pair[0]==pair[1],((read,write,tail,header),pair[0][0],pair[1][0])
print('PASS_RING_PERSIST_APPEND_NATIVE 3')
