#!/usr/bin/env python3
"""Bounded original Apollo 0x491f54 versus C begin-core header comparison."""
import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP, UC_ARM_REG_LR

BASE=0x438000
BLOB='g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
blob=open(BLOB,'rb').read()[32:]
source=Path('g2/components/audio/uart_thread_source_candidate/module_begin_core.c')
temporary=tempfile.TemporaryDirectory(prefix='g2-tinyframe-header-')
stub=Path(temporary.name)/'stubs.c'
shared=Path(temporary.name)/'begin-core.so'
stub.write_text('''#include <stdint.h>
uint32_t audio_log_flags(void){return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,
                        uint32_t e,const char*f,...){
 (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...){
 (void)a;(void)b;(void)c;return 0;}
''')
subprocess.run(['clang','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',
                str(source),str(stub),'-o',str(shared)],check=True)
lib=ctypes.CDLL(str(shared))
fn=lib.audio_uart_module_begin_core
fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint16]
fn.restype=ctypes.c_uint32
cases=0
for master in (0,1):
 for prior in (0,1,0x7fff,0xffff):
  for mode in (0,1):
   for size in (0,1,0x2a,0xffff):
    for kind in (0,1,0x12,0xffff):
     tf=ctypes.create_string_buffer(0x7160)
     frame=ctypes.create_string_buffer(24)
     ctypes.memmove(ctypes.addressof(tf)+0xc,bytes([master]),1)
     ctypes.memmove(ctypes.addressof(tf)+0xe,struct.pack('<H',prior),2)
     ctypes.memmove(ctypes.addressof(frame)+0,struct.pack('<H',0x1234),2)
     ctypes.memmove(ctypes.addressof(frame)+2,bytes([mode]),1)
     ctypes.memmove(ctypes.addressof(frame)+4,struct.pack('<H',kind),2)
     ctypes.memmove(ctypes.addressof(frame)+12,struct.pack('<H',size),2)
     assert fn(tf,frame,None,None,50)==1
     expected=(ctypes.string_at(ctypes.addressof(tf)+0x6021,9),
               ctypes.string_at(ctypes.addressof(tf)+0xe,2),
               ctypes.string_at(ctypes.addressof(frame),2))
     uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
     uc.mem_map(BASE,(len(blob)+0xfff)&~0xfff);uc.mem_write(BASE,blob)
     uc.mem_map(0x20000000,0x20000);uc.mem_map(0x100000,0x1000)
     t=0x20000000;f=0x20008000
     uc.mem_write(t+0xc,bytes([master]));uc.mem_write(t+0xe,struct.pack('<H',prior))
     uc.mem_write(f,struct.pack('<H',0x1234));uc.mem_write(f+2,bytes([mode]))
     uc.mem_write(f+4,struct.pack('<H',kind));uc.mem_write(f+12,struct.pack('<H',size))
     uc.reg_write(UC_ARM_REG_R0,t);uc.reg_write(UC_ARM_REG_R1,t+0x6021)
     uc.reg_write(UC_ARM_REG_R2,f);uc.reg_write(UC_ARM_REG_SP,0x2001f000)
     uc.reg_write(UC_ARM_REG_LR,0x100001)
     uc.hook_add(UC_HOOK_CODE,lambda u,a,s,_:u.emu_stop() if a==0x100000 else None)
     uc.emu_start(0x491f55,0x100002,count=10000)
     got=(bytes(uc.mem_read(t+0x6021,9)),bytes(uc.mem_read(t+0xe,2)),
          bytes(uc.mem_read(f,2)))
     assert got==expected,(master,prior,mode,size,kind,expected,got)
     assert uc.reg_read(UC_ARM_REG_R0)==9
     cases+=1
print(f'PASS {cases} TinyFrame header original-byte/C comparisons')
