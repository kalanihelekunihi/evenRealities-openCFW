"""Bounded original-byte versus compiled-C FreeType cache hook comparators."""
from pathlib import Path
import ctypes, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
RETURN=0x600000
def stock(address,left,right):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    u.mem_write(0x20010000,b''.join(x.to_bytes(4,'little') for x in left))
    u.mem_write(0x20010020,b''.join(x.to_bytes(4,'little') for x in right))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,0x20010000);u.reg_write(UC_ARM_REG_R1,0x20010020)
    u.emu_start(address|1,RETURN,count=1000)
    result=u.reg_read(UC_ARM_REG_R0)
    return result if result<0x80000000 else result-0x100000000

STUBS='''#include <stdint.h>
uint32_t audio_uart_font_glyph_cache_initialize(void *a,void *b){(void)a;(void)b;return 0;}
uint32_t audio_uart_font_bitmap_cache_initialize(void *a,void *b){(void)a;(void)b;return 0;}
uint32_t audio_uart_font_outline_cache_initialize(void *a,void *b){(void)a;(void)b;return 0;}
void audio_uart_font_bitmap_release(void *a){(void)a;}
void *audio_uart_font_outline_context(void){return 0;}
void audio_uart_font_outline_release(void *a,void *b){(void)a;(void)b;}
'''
cases=[((0,0),(0,0)),((1,2),(1,2)),((1,0),(2,0)),((2,0),(1,0)),
       ((1,2),(1,3)),((1,3),(1,2)),((0xffffffff,0),(0,0)),
       ((0,0xffffffff),(0,0)),((0,0),(0,0xffffffff))]
with tempfile.TemporaryDirectory() as d:
    stub=Path(d)/'stubs.c';stub.write_text(STUBS)
    so=Path(d)/'hooks.so'
    source=ROOT/'components/audio/uart_thread_source_candidate/display_font_cache_hooks.c'
    subprocess.run(['clang','-shared','-fPIC','-O2',str(source),str(stub),'-o',str(so)],check=True)
    lib=ctypes.CDLL(str(so))
    for address,name in ((0x52977a,'audio_uart_font_cache_compare_pair'),
                         (0x529aee,'audio_uart_font_cache_compare_pair'),
                         (0x529d50,'audio_uart_font_cache_compare_outline')):
        fn=getattr(lib,name);fn.argtypes=[ctypes.c_void_p,ctypes.c_void_p];fn.restype=ctypes.c_int32
        for left,right in cases:
            a=(ctypes.c_uint32*2)(*left);b=(ctypes.c_uint32*2)(*right)
            got=fn(a,b);want=stock(address,left,right)
            assert got==want,(hex(address),left,right,got,want)
        print(f'PASS {len(cases)}/{len(cases)} {hex(address)} original-byte/compiled-C')
