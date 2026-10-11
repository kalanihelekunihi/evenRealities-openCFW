"""Bounded native-byte check of font_manager_get_font (0x46cf56)."""
from pathlib import Path
import struct
import ctypes
import subprocess
import tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_R0,UC_ARM_REG_SP
from unicorn.unicorn_const import UC_HOOK_CODE
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
LIST=0x20001000
RETURN=0x600000

def stock(handle,first):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000)
    u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    u.mem_write(LIST,struct.pack('<III',first,0,0))
    u.reg_write(UC_ARM_REG_SP,0x200ff000)
    u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,handle)
    last=[0]
    def hook(m,a,s,userdata):
        last[0]=a
        if a==RETURN:m.emu_stop()
        elif a==0x43d0ce: # audio_log_flags, controlled no-log branch
            m.reg_write(UC_ARM_REG_R0,0)
            m.reg_write(UC_ARM_REG_PC,m.reg_read(UC_ARM_REG_LR))
    u.hook_add(UC_HOOK_CODE,hook)
    try:u.emu_start(0x46cf57,RETURN,count=10000)
    except Exception as exc:raise RuntimeError(f'{exc} at {last[0]:#x}') from exc
    return u.reg_read(UC_ARM_REG_R0)

with tempfile.TemporaryDirectory() as d:
    stub=Path(d)/'stub.c'
    stub.write_text('''
#include <stdint.h>
uint32_t audio_log_flags(void) { return 0; }
void audio_log_extended(uint8_t a,const char*b,const char*c,const char*d,
                        uint32_t e,const char*f,...) {(void)a;(void)b;(void)c;(void)d;(void)e;(void)f;}
uint32_t compressed_log_output(uint32_t a,const char*b,const char*c,...) {
    (void)a;(void)b;(void)c;return 0;
}
''')
    so=Path(d)/'head.so'
    source=ROOT/'components/audio/uart_thread_source_candidate/display_ring_head.c'
    subprocess.run(['clang','-shared','-fPIC','-O2',str(source),str(stub),'-o',str(so)],check=True)
    fn=ctypes.CDLL(str(so)).audio_uart_display_ring_head
    fn.argtypes=[ctypes.POINTER(ctypes.c_uint32)]
    fn.restype=ctypes.c_void_p
    cases=[(LIST,0),(LIST,0x20002000),(0,0x20002000)]
    for handle,first in cases:
        cell=(ctypes.c_uint32*3)(first,0,0)
        actual=stock(handle,first)
        expected=fn(cell if handle else None) or 0
        assert actual==expected,(handle,first,actual,expected)
print(f'PASS {len(cases)}/{len(cases)} original-byte/compiled-C font-head cuts')
