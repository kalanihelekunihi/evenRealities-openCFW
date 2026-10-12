#!/usr/bin/env python3
"""Compare bounded stock and compiled ARM C persistence initialization effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_persist_initialize.c'
STUB='''#include <stdint.h>
volatile uint8_t audio_uart_ring_persist_initialized,audio_uart_ring_persist_has_tail;
uint8_t audio_uart_ring_persist_queue_state[24];
uint32_t audio_uart_ring_persist_validate_48e900(void){return 0;}
void audio_uart_ring_persist_reset_48e99c(void){}
uint32_t audio_uart_ring_persist_read_clock_47dcec(void){return 0;}
uint32_t audio_uart_ring_persist_read_version_47dd08(void){return 0;}
void audio_uart_ring_persist_submit_48ea66(uint32_t a,uint32_t b,const void*c){(void)a;(void)b;(void)c;}
'''
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_persist_initialize_48eac8',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for already,valid,tail in ((1,0,0),(0,0,0),(0,1,0),(0,1,1)):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   flag=sym['audio_uart_ring_persist_initialized'] if is_c else 0x20075032
   has=sym['audio_uart_ring_persist_has_tail'] if is_c else 0x20075033
   queue=sym['audio_uart_ring_persist_queue_state'] if is_c else 0x200771f4
   u.mem_write(flag,bytes([already]));u.mem_write(has,b'\x07')
   u.mem_write(queue+8,(12).to_bytes(4,'little'));u.mem_write(queue+16,(0 if tail else 12).to_bytes(4,'little'))
   trace=[]
   hooks=[('validate','audio_uart_ring_persist_validate_48e900',0x48e900),('reset','audio_uart_ring_persist_reset_48e99c',0x48e99c),('clock','audio_uart_ring_persist_read_clock_47dcec',0x47dcec),('version','audio_uart_ring_persist_read_version_47dd08',0x47dd08),('submit','audio_uart_ring_persist_submit_48ea66',0x48ea66)]
   for name,symbol,native in hooks:
    addr=sym[symbol] if is_c else native
    def hook(uc,pc,size,user,name=name):
     if name=='validate':trace.append(('validate',));uc.reg_write(UC_ARM_REG_R0,valid)
     elif name=='reset':trace.append(('reset',))
     elif name=='clock':trace.append(('clock',));uc.reg_write(UC_ARM_REG_R0,0x12345678)
     elif name=='version':trace.append(('version',));uc.reg_write(UC_ARM_REG_R0,0x9abcdef0)
     else:
      ptr=uc.reg_read(UC_ARM_REG_R2)
      trace.append(('submit',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),bytes(uc.mem_read(ptr,8))))
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.emu_start((sym['audio_uart_ring_persist_initialize_48eac8'] if is_c else 0x48eac8)|1,0x600000,count=3000)
   pair.append((bytes(u.mem_read(flag,1)),bytes(u.mem_read(has,1)),trace))
  assert pair[0]==pair[1],((already,valid,tail),pair)
print('PASS_RING_PERSIST_INITIALIZE_NATIVE 4')
