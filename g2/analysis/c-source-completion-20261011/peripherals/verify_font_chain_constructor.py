"""Bounded original-byte / compiled-C invalid font-chain constructor cuts."""
from pathlib import Path
import ctypes,struct,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
from unicorn.unicorn_const import UC_HOOK_CODE
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
DESC=0x20001000
RETURN=0x600000

def stock(pointer,count):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000);u.mem_write(DESC,b'\0'*48)
    u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,pointer)
    u.reg_write(UC_ARM_REG_R1,count)
    last=[0];allocs=[0]
    def hook(m,a,s,userdata):
        last[0]=a
        if a==RETURN:m.emu_stop()
        elif a==0x474cd2:
            allocs[0]+=1
            m.reg_write(UC_ARM_REG_R0,0)
            m.reg_write(UC_ARM_REG_PC,m.reg_read(UC_ARM_REG_LR))
        elif a==0x43d0ce: # log flags, no-log branch
            m.reg_write(UC_ARM_REG_R0,0)
            m.reg_write(UC_ARM_REG_PC,m.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start(0x46cae1,RETURN,count=20000)
    except Exception as exc:raise RuntimeError(f'{exc} at {last[0]:#x}') from exc
    return u.reg_read(UC_ARM_REG_R0),allocs[0]

with tempfile.TemporaryDirectory() as d:
    stub=Path(d)/'stub.c'
    stub.write_text('''
#include <stdint.h>
#include <stddef.h>
void *file_heap_allocate(uint32_t n) {(void)n;return 0;}
void file_heap_free(void *p) {(void)p;}
uint32_t audio_log_flags(void) {return 0;}
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,uint32_t e,const char*f,...) {
 (void)a;(void)b;(void)c;(void)d;(void)e;(void)f;
}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...) {
 (void)a;(void)b;(void)c;return 0;
}
void *audio_uart_font_create(const char *a,uint8_t b,uint32_t c,uint8_t d) {
 (void)a;(void)b;(void)c;(void)d;return 0;
}
void audio_uart_font_delete(void *a) {(void)a;}
''')
    so=Path(d)/'ctor.so'
    source=ROOT/'components/audio/uart_thread_source_candidate/display_ring_constructor.c'
    subprocess.run(['clang','-shared','-fPIC','-O2',str(source),str(stub),'-o',str(so)],check=True)
    fn=ctypes.CDLL(str(so)).audio_uart_display_ring_construct
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint8),ctypes.c_uint32]
    fn.restype=ctypes.c_void_p
    data=(ctypes.c_uint8*48)()
    cases=[(0,4),(DESC,0),(DESC,9),(DESC,8)]
    for pointer,count in cases:
        actual,allocations=stock(pointer,count)
        expected=fn(data if pointer else None,count) or 0
        assert actual==expected,(pointer,count,actual,expected)
        assert allocations==(1 if count==8 else 0),(pointer,count,allocations)
print(f'PASS {len(cases)}/{len(cases)} original-byte/compiled-C font-chain invalid/allocation-failure cuts')
