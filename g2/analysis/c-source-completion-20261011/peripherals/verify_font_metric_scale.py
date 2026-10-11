"""Original-byte versus compiled-C FreeType fixed-point scale."""
from pathlib import Path
import ctypes,random,subprocess,tempfile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR,UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
RETURN=0x600000

def stock(a,b):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    u.reg_write(UC_ARM_REG_R0,a&0xffffffff);u.reg_write(UC_ARM_REG_R1,b&0xffffffff)
    u.emu_start(0x5246f9,RETURN,count=5000)
    x=u.reg_read(UC_ARM_REG_R0)
    return x if x<0x80000000 else x-0x100000000

with tempfile.TemporaryDirectory() as d:
    so=Path(d)/'scale.so'
    source=ROOT/'components/audio/uart_thread_source_candidate/display_font_metric_scale.c'
    subprocess.run(['clang','-shared','-fPIC','-O2',str(source),'-o',str(so)],check=True)
    fn=ctypes.CDLL(str(so)).audio_uart_font_scale_metric
    fn.argtypes=[ctypes.c_uint32,ctypes.c_int32];fn.restype=ctypes.c_int32
    cases=[(0,0),(1,1),(-1,1),(1,-1),(-1,-1),(0x1fff,65536),
           (0x7fffffff,0x7fffffff),(-0x80000000,65536)]
    rng=random.Random(0x5246f8)
    cases += [(rng.randrange(-0x80000000,0x80000000),
               rng.randrange(-0x80000000,0x80000000)) for _ in range(128)]
    for a,b in cases:
        actual=stock(a,b);expected=fn(a&0xffffffff,b)
        assert actual==expected,(a,b,actual,expected)
print(f'PASS {len(cases)}/{len(cases)} original-byte/compiled-C fixed-point scale cuts')
