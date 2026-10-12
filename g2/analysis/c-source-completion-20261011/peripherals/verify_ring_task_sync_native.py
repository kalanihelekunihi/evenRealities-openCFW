#!/usr/bin/env python3
"""Stock/C start/end synchronization, selected child ABI controlled."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3];B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_task_sync.c'
STUB='''#include <stdint.h>
uint8_t audio_uart_thread_manager_state[64];
uint32_t audio_flags_wait(uint32_t a,uint32_t b,uint32_t c){(void)a;(void)b;(void)c;return 0;}
uint32_t g2_log_event_set_task(uint32_t a,uint32_t b){(void)a;return b;}
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char *b,const char *c,const char *d,uint32_t e,const char *f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
'''
def w(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def s(u,a):return bytes(u.mem_read(a,150)).split(b'\0')[0].decode('ascii')
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_ring_state_transition_4c9b86',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(v['p_vaddr'],v.data()) for v in e.iter_segments() if v['p_type']=='PT_LOAD'];sym={v.name:v['st_value'] for v in e.get_section_by_name('.symtab').iter_symbols()}
 for name,native in [('audio_uart_ring_state_transition_4c9b86',0x4c9b86),('audio_uart_ring_resource_transition_4c9be2',0x4c9be2)]:
  for level in (0,1,2,4,7):
   pair=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in seg:u.mem_write(a,d)
    cell=sym['audio_uart_thread_manager_state'] if is_c else 0x200040d8
    u.mem_write(cell+0x1c,struct.pack('<I',0x2007f100))
    trace=[]
    hooks=[('audio_flags_wait',0x4492c2),('g2_log_event_set_task',0x4495e4),('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e)]
    for h,na in hooks:
     addr=sym[h] if is_c else na
     def hook(uc,address,size,data,h=h):
      a,b,c,d=[uc.reg_read(v) for v in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
      sp=uc.reg_read(UC_ARM_REG_SP)
      if h=='audio_flags_wait':trace.append((h,a,b,c));uc.reg_write(UC_ARM_REG_R0,0x800000)
      elif h=='g2_log_event_set_task':trace.append((h,a,b));uc.reg_write(UC_ARM_REG_R0,b)
      elif h=='audio_log_flags':trace.append((h,));uc.reg_write(UC_ARM_REG_R0,level)
      elif h=='audio_log_extended':trace.append((h,a,s(uc,b),s(uc,c),s(uc,d),w(uc,sp),s(uc,w(uc,sp+4)),w(uc,sp+8)))
      else:trace.append((h,a,s(uc,b),s(uc,c),d))
      uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
     u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,6)
    u.emu_start((sym[name] if is_c else native)|1,0x600000,count=3000)
    pair.append((trace,u.reg_read(UC_ARM_REG_R0)))
   assert pair[0]==pair[1],(name,level,pair)
 print('PASS_RING_TASK_SYNC_NATIVE',10)
