#!/usr/bin/env python3
"""Compare stock and compiled ARM C persistence submit record composition."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_persist_submit.c'
STUB='''#include <stdint.h>
volatile uint8_t audio_uart_ring_persist_early_pending;
uint32_t audio_uart_ring_persist_early_check_47dcb4(uint8_t*p){(void)p;return 0;}
uint32_t audio_uart_ring_persist_clock_snapshot_47dc74(void){return 0;}
void audio_uart_ring_persist_append_48e9be(uint32_t a,uint32_t b,const uint32_t*c,uint32_t d){(void)a;(void)b;(void)c;(void)d;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_persist_submit_48ea66',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for early,pending in ((0,0),(1,0),(1,1)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cell=sym['audio_uart_ring_persist_early_pending'] if is_c else 0x20075034
   u.mem_write(cell,bytes([pending]));payload=0x20090000;u.mem_write(payload,b'\x01\x02\x03\x04\x05\x06\x07\x08')
   trace=[]
   hooks=[('check','audio_uart_ring_persist_early_check_47dcb4',0x47dcb4),('clock','audio_uart_ring_persist_clock_snapshot_47dc74',0x47dc74),('append','audio_uart_ring_persist_append_48e9be',0x48e9be)]
   for name,symbol,native in hooks:
    addr=sym[symbol] if is_c else native
    def hook(uc,pc,size,user,name=name):
     if name=='check':
      uc.mem_write(uc.reg_read(UC_ARM_REG_R0),bytes([early]));uc.reg_write(UC_ARM_REG_R0,0x11223344)
     elif name=='clock':uc.reg_write(UC_ARM_REG_R0,0x55667788)
     else:
      key=uc.reg_read(UC_ARM_REG_R0);count=uc.reg_read(UC_ARM_REG_R1);data=uc.reg_read(UC_ARM_REG_R2);stamp=uc.reg_read(UC_ARM_REG_R3)
      trace.append((key,count,bytes(uc.mem_read(data,count*4)),stamp))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x60102);u.reg_write(UC_ARM_REG_R1,2);u.reg_write(UC_ARM_REG_R2,payload);u.reg_write(UC_ARM_REG_R3,0xdeadbeef)
   u.emu_start((sym['audio_uart_ring_persist_submit_48ea66'] if is_c else 0x48ea66)|1,0x600000,count=3000)
   pair.append((trace,bytes(u.mem_read(cell,1))))
  assert pair[0]==pair[1],((early,pending),pair)
print('PASS_RING_PERSIST_SUBMIT_NATIVE 3')
