"""Original-byte versus compiled-C font glyph descriptor cache callback cuts."""
from pathlib import Path
import ctypes,struct,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_SP
from unicorn.unicorn_const import UC_HOOK_CODE
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
CACHE=0x20324600;FLAG=0x20074fe3;DEST=0x20001000;RETURN=0x600000
PATTERN=bytes(range(32))

def stock(gate,address,hit,previous):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000);u.mem_map(0x20300000,0x40000)
    u.mem_write(FLAG,bytes([gate]));u.mem_write(DEST,b'?'*32)
    entry=CACHE+(address&0x1ff)*40
    if hit:
        u.mem_write(entry,struct.pack('<I',address)+bytes([5,0,0,0])+b'Z'*32)
    u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,0x20002000)
    u.reg_write(UC_ARM_REG_R1,DEST)
    u.reg_write(UC_ARM_REG_R2,address)
    u.reg_write(UC_ARM_REG_R3,previous)
    calls=[0];last=[0]
    def hook(m,a,s,user):
        last[0]=a
        if a==RETURN:m.emu_stop()
        elif a==0x4b26a4:
            calls[0]+=1
            m.mem_write(m.reg_read(UC_ARM_REG_R1),PATTERN)
            m.reg_write(UC_ARM_REG_R0,7)
            m.reg_write(UC_ARM_REG_PC,m.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start(0x46d239,RETURN,count=100000)
    except Exception as exc:raise RuntimeError(f'{exc} at {last[0]:#x}') from exc
    return (u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DEST,32)),
            bytes(u.mem_read(entry,40)),calls[0])

with tempfile.TemporaryDirectory() as d:
    stub=Path(d)/'stub.c'
    stub.write_text('''
#include <stdint.h>
#include <string.h>
uint8_t audio_uart_ring_config_idle;
uint8_t audio_uart_ring_config_workspace[0x5000];
uint32_t raw_calls;
uint32_t audio_uart_font_glyph_descriptor(void*a,void*b,uint32_t c,uint32_t d) {
 (void)a;(void)c;(void)d;raw_calls++;for(uint32_t i=0;i<32;i++)((uint8_t*)b)[i]=(uint8_t)i;return 7;
}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c) {return memcpy(a,b,c);}
''')
    so=Path(d)/'read.so'
    source=ROOT/'components/audio/uart_thread_source_candidate/display_font_glyph_cache.c'
    subprocess.run(['clang','-shared','-fPIC','-O2',str(source),str(stub),'-o',str(so)],check=True)
    lib=ctypes.CDLL(str(so));fn=lib.audio_uart_font_glyph_cache_callback
    fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_uint32]
    fn.restype=ctypes.c_uint32
    flag=ctypes.c_uint8.in_dll(lib,'audio_uart_ring_config_idle')
    cache=(ctypes.c_uint8*0x5000).in_dll(lib,'audio_uart_ring_config_workspace')
    calls=ctypes.c_uint32.in_dll(lib,'raw_calls')
    cases=[(0,0x2123,False,0),(1,0,False,0),(1,0x2123,True,0),
           (1,0x2123,False,0x44)]
    for gate,address,hit,previous in cases:
        ctypes.memset(cache,0,0x5000)
        flag.value=gate;calls.value=0
        dest=(ctypes.c_uint8*32)(*([ord('?')]*32))
        index=(address&0x1ff)*40
        if hit:
            entry=struct.pack('<I',address)+bytes([5,0,0,0])+b'Z'*32
            for i,x in enumerate(entry):cache[index+i]=x
        actual=stock(gate,address,hit,previous)
        status=fn(None,dest,address,previous)
        expected=(status,bytes(dest),bytes(cache[index:index+40]),calls.value)
        assert actual==expected,(gate,address,hit,actual,expected)
print(f'PASS {len(cases)}/{len(cases)} original-byte/compiled-C font glyph cache cuts')
