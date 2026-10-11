#!/usr/bin/env python3
"""Bounded stock/C TinyFrame payload and close comparison; flush is a capture cut."""
import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_SP,UC_ARM_REG_LR
BASE=0x438000
blob=open('g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin','rb').read()[32:]
source=Path('g2/components/audio/uart_thread_source_candidate/module_payload_close.c')
with tempfile.TemporaryDirectory(prefix='g2-tinyframe-payload-') as tmp:
 stub=Path(tmp)/'stub.c'; shared=Path(tmp)/'payload.so'
 stub.write_text('''#include <stdint.h>
static uint8_t packets[16][0x400]; static uint32_t lengths[16],count;
uint32_t audio_uart_sync_send(const void *p,uint32_t n,uint32_t t){
 (void)t;if(count<16){lengths[count]=n;const uint8_t *s=p;
 for(uint32_t i=0;i<n && i<0x400;i++)packets[count][i]=s[i];count++;}return 0;}
void tf_reset(void){count=0;}
uint32_t tf_count(void){return count;}
uint32_t tf_len(uint32_t i){return lengths[i];}
const uint8_t *tf_packet(uint32_t i){return packets[i];}
''')
 subprocess.run(['clang','-shared','-fPIC','-O2','-Wall','-Wextra','-Werror',
                 str(source),str(stub),'-o',str(shared)],check=True)
 lib=ctypes.CDLL(str(shared))
 payload=lib.audio_uart_module_payload_core;payload.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32]
 close=lib.audio_uart_module_close_core;close.argtypes=[ctypes.c_void_p]
 lib.tf_packet.restype=ctypes.c_void_p;lib.tf_packet.argtypes=[ctypes.c_uint32]
 lib.tf_len.argtypes=[ctypes.c_uint32]
 cases=0
 for initial in (0,8,1022,1023):
  for n in (0,1,2,17,256,1024,1031):
   for expected in (0,1,256):
    data=bytes((i*7+13)&255 for i in range(n))
    seed=bytearray(0x7160)
    for i in range(initial):seed[0x6021+i]=(i*3+5)&255
    struct.pack_into('<I',seed,0x6424,initial)
    struct.pack_into('<I',seed,0x6428,expected)
    struct.pack_into('<H',seed,0x642c,0x1234)
    seed[0x642e]=1
    tf=ctypes.create_string_buffer(bytes(seed),len(seed))
    src=ctypes.create_string_buffer(data,max(1,n))
    lib.tf_reset();payload(tf,src,n);close(tf)
    cstate=ctypes.string_at(tf,len(seed))
    cpack=[ctypes.string_at(lib.tf_packet(i),lib.tf_len(i)) for i in range(lib.tf_count())]
    uc=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    uc.mem_map(BASE,(len(blob)+0xfff)&~0xfff);uc.mem_write(BASE,blob)
    uc.mem_map(0x20000000,0x20000);uc.mem_map(0x100000,0x1000)
    uc.mem_write(0x4d9522,b'\x70\x47') # capture-only BX LR at physical UART flush
    t=0x20000000;s=0x20010000;uc.mem_write(t,bytes(seed));uc.mem_write(s,data)
    npack=[]
    def hook(u,a,size,_):
     if a==0x100000:u.emu_stop()
     elif a==0x4d9522:
      p=u.reg_read(UC_ARM_REG_R1);q=u.reg_read(UC_ARM_REG_R2)
      npack.append(bytes(u.mem_read(p,q)))
    uc.hook_add(UC_HOOK_CODE,hook)
    for address,args in ((0x492114,(t,s,n)),(0x492198,(t,0,0))):
     uc.reg_write(UC_ARM_REG_R0,args[0]);uc.reg_write(UC_ARM_REG_R1,args[1]);uc.reg_write(UC_ARM_REG_R2,args[2]);uc.reg_write(UC_ARM_REG_SP,0x2001f000);uc.reg_write(UC_ARM_REG_LR,0x100001)
     uc.emu_start(address|1,0x100002,count=300000)
    nstate=bytes(uc.mem_read(t,len(seed)))
    for lo,hi in ((0x6021,0x642f),):
     assert cstate[lo:hi]==nstate[lo:hi],(initial,n,expected,'state',lo)
    assert cpack==npack,(initial,n,expected,'flush',len(cpack),len(npack))
    cases+=1
 print(f'PASS {cases} TinyFrame payload/close original-byte/C comparisons, flush captured')
