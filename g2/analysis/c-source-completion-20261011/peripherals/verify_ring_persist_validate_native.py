#!/usr/bin/env python3
"""Execute stock and compiled C persistence ring validator on bounded states."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_persist_buffer.c'
STUB='''#include <stdint.h>
uint8_t audio_uart_ring_persist_storage[4096];
uint8_t audio_uart_ring_persist_queue_state[24];
'''
def write32(uc,a,v):uc.mem_write(a,int(v).to_bytes(4,'little'))
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_persist_validate_48e900',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 cases=[(0x31435054,0,0,0,0),(0x31435054,0,12,0,0),(0x31435054,0,12,0,0xa1),(0x31435054,0,12,0,0xb1),(0,0,0,0,0),(0x31435054,1,0,0,0),(0x31435054,0,0x1004,0,0)]
 for magic,read,write,tail,header in cases:
  results=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   q=sym['audio_uart_ring_persist_queue_state'] if is_c else 0x200771f4
   storage=sym['audio_uart_ring_persist_storage'] if is_c else 0x200761f4
   for offset,value in ((0,magic),(4,0x1000),(8,write),(12,read),(16,tail)):
    write32(u,q+offset,value)
   write32(u,storage,header)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_persist_validate_48e900'] if is_c else 0x48e900)|1,0x600000,count=10000)
   results.append(u.reg_read(UC_ARM_REG_R0))
  assert results[0]==results[1],((magic,read,write,tail,header),results)
print('PASS_RING_PERSIST_VALIDATE_NATIVE',len(cases))
