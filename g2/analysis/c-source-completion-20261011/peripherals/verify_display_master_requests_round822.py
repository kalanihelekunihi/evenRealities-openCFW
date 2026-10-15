#!/usr/bin/env python3
"""Bounded native/C comparison of Apollo master display request wrappers."""
from pathlib import Path
import hashlib
import struct
import subprocess
import tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *

root=Path(__file__).resolve().parents[3]
blob=(root/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest()=='19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
src=root/'components/audio/uart_thread_source_candidate/display_master_requests.c'
stubs='''#include <stdint.h>
uint32_t audio_log_level(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){(void)a;(void)b;(void)c;return 0;}
int32_t audio_uart_master_request_core_464772(uint32_t a,const void*b,uint32_t c,uint32_t d,uint32_t e,uint32_t f,uint32_t g){(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;(void)g;return 0;}
'''
entries=[('audio_uart_master_display_start',0x464b2e),
         ('audio_uart_master_display_refresh',0x464bb2),
         ('audio_uart_master_display_stop',0x464c36),
         ('audio_uart_master_control',0x464cba)]
with tempfile.TemporaryDirectory() as d:
 tmp=Path(d);stub=tmp/'stub.c';stub.write_text(stubs);elf=tmp/'fixture.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_master_display_start',str(src),str(stub),'-o',str(elf)],check=True)
 with elf.open('rb') as f:
  e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
  syms={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
 for name,native in entries:
  for app_id in (0,0x1234,0x12345678):
   for length in (0,1,0x2800,0xffff):
    for level in (0,1,2,4,7):
     pair=[]
     for compiled in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
      u.mem_map(0x400000,0x400000);u.mem_write(0x438000,blob)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
      for address,data in segments:u.mem_write(address,data)
      trace=[]
      for kind,symbol,address in [('level','audio_log_level',0x43d0ce),
                                  ('extended','audio_log_extended',0x43d574),
                                  ('compact','compressed_log_output',0x43ce9e),
                                  ('core','audio_uart_master_request_core_464772',0x464772)]:
       hook_addr=syms[symbol] if compiled else address
       def hook(uc,pc,width,user,kind=kind):
        regs=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
        if kind=='level':trace.append(('level',));uc.reg_write(UC_ARM_REG_R0,level)
        elif kind=='extended':trace.append(('extended',regs[0]))
        elif kind=='compact':trace.append(('compact',regs[0]))
        else:
         stack=struct.unpack('<III',uc.mem_read(uc.reg_read(UC_ARM_REG_SP),12))
         trace.append(('core',regs,stack))
         uc.reg_write(UC_ARM_REG_R0,0)
        uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
       u.hook_add(UC_HOOK_CODE,hook,begin=hook_addr&~1,end=hook_addr&~1)
      u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
      args=((0x87654321,) if name=='audio_uart_master_control' else
            (app_id,0x20080000,length,0x87654321))
      for reg,arg in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3),args):u.reg_write(reg,arg)
      u.emu_start((syms[name] if compiled else native)|1,0x600000,count=10000)
      pair.append(trace)
     assert pair[0]==pair[1],(name,app_id,length,level,pair)
print('PASS_DISPLAY_MASTER_REQUESTS_NATIVE',len(entries)*3*4*5)
