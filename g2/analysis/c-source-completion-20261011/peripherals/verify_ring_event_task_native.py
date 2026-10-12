#!/usr/bin/env python3
"""Stock/C ring event task logging and thread flags with controlled children."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
R=Path(__file__).resolve().parents[3]
B=(R/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
S=R/'components/audio/uart_thread_source_candidate/display_ring_event_task.c'
STUB='''#include <stdint.h>
struct ring_thread_manager {unsigned char reserved[8];void *thread;};
struct ring_thread_manager audio_uart_ring_thread_manager;
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t x,const char *a,const char *b,const char *c,uint32_t d,const char *e,...){(void)x;(void)a;(void)b;(void)c;(void)d;(void)e;}
uint32_t compressed_log_output(uint32_t a,const char *b,const char *c,...){(void)a;(void)b;(void)c;return 0;}
uint32_t audio_thread_flags_set(void *p,uint32_t x){(void)p;return x;}
'''
def word(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
def cstr(u,a):
 data=bytes(u.mem_read(a,160));return data.split(b'\0')[0].decode('ascii')
with tempfile.TemporaryDirectory() as td:
 t=Path(td);stub=t/'stub.c';stub.write_text(STUB);elf=t/'c.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,Thread_SendEvtToRingTask',str(S),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);seg=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for level in (0,1,2,4,7):
  pair=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
   u.mem_map(0x400000,0x400000);u.mem_write(0x438000,B);u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in seg:u.mem_write(a,d)
   cell=sym['audio_uart_ring_thread_manager'] if is_c else 0x20004120
   u.mem_write(cell+8,struct.pack('<I',0x2007f100))
   hooks=[('audio_log_flags',0x43d0ce),('audio_log_extended',0x43d574),('compressed_log_output',0x43ce9e),('audio_thread_flags_set',0x449238)]
   trace=[]
   for name,native in hooks:
    addr=sym[name] if is_c else native
    def hook(uc,address,size,data,name=name):
     r=[uc.reg_read(x) for x in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)]
     sp=uc.reg_read(UC_ARM_REG_SP)
     if name=='audio_log_flags':trace.append(('flags',));uc.reg_write(UC_ARM_REG_R0,level)
     elif name=='audio_log_extended':trace.append(('extended',r[0],*[cstr(uc,v) for v in r[1:]],word(uc,sp),cstr(uc,word(uc,sp+4)),word(uc,sp+8)))
     elif name=='compressed_log_output':trace.append(('compressed',r[0],cstr(uc,r[1]),cstr(uc,r[2]),r[3]))
     else:trace.append(('set',r[0],r[1]));uc.reg_write(UC_ARM_REG_R0,r[1])
     uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook,begin=addr&~1,end=addr&~1)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,0x19)
   u.emu_start((sym['Thread_SendEvtToRingTask'] if is_c else 0x4c543e)|1,0x600000,count=3000)
   pair.append((trace,u.reg_read(UC_ARM_REG_R0)))
  assert pair[0]==pair[1],(level,pair)
 print('PASS_RING_EVENT_TASK_NATIVE',5)
