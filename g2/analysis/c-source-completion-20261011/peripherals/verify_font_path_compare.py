"""Original-byte versus compiled-C font pathname comparison."""
from pathlib import Path
import ctypes,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
LEFT,RIGHT,RETURN=0x20001000,0x20002000,0x600000

def stock(left,right):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    u.mem_write(LEFT,left+b'\0');u.mem_write(RIGHT,right+b'\0')
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,LEFT);u.reg_write(UC_ARM_REG_R1,RIGHT)
    u.emu_start(0x46cacd,RETURN,count=5000)
    value=u.reg_read(UC_ARM_REG_R0)
    return value if value<0x80000000 else value-0x100000000

with tempfile.TemporaryDirectory() as d:
    stub=Path(d)/'stub.c'
    stub.write_text('''
#include <stdint.h>
uint32_t g2_log_module_length(const char*a){uint32_t n=0;while(a[n])n++;return n;}
void *audio_uart_lv_malloc(uint32_t a){(void)a;return 0;}
void *audio_queue_copy_bytes(void*a,const void*b,uint32_t c){(void)b;(void)c;return a;}
''')
    so=Path(d)/'path.so'
    source=ROOT/'components/audio/uart_thread_source_candidate/display_font_path_children.c'
    subprocess.run(['clang','-shared','-fPIC','-O2',str(source),str(stub),'-o',str(so)],check=True)
    fn=ctypes.CDLL(str(so)).audio_uart_font_path_compare
    fn.argtypes=[ctypes.c_char_p,ctypes.c_char_p];fn.restype=ctypes.c_int32
    cases=[(b'',b''),(b'a',b'a'),(b'ab',b'ac'),(b'ab',b'a'),
           (b'a',b'ab'),(b'ABC',b'abc'),(b'\xff',b'\x01')]
    for left,right in cases:
        actual=stock(left,right);expected=fn(left,right)
        assert actual==expected,(left,right,actual,expected)
print(f'PASS {len(cases)}/{len(cases)} original-byte/compiled-C font path compare cuts')
