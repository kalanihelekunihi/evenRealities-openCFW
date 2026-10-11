"""Original-byte versus actual compiled C FreeType MulDiv and DivFix."""
from pathlib import Path
import ctypes, random, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
RETURN=0x600000
def stock(address,args):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
    u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x20000000,0x100000)
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
    for reg,value in zip((UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2),args):
        u.reg_write(reg,value&0xffffffff)
    u.emu_start(address|1,RETURN,count=10000)
    value=u.reg_read(UC_ARM_REG_R0)
    return value if value<0x80000000 else value-0x100000000

with tempfile.TemporaryDirectory() as d:
    so=Path(d)/'math.so'
    source=ROOT/'components/audio/uart_thread_source_candidate/display_font_math.c'
    subprocess.run(['clang','-shared','-fPIC','-O2',str(source),'-o',str(so)],check=True)
    lib=ctypes.CDLL(str(so))
    cases=[(0,0,1),(1,1,1),(-1,1,1),(1,-1,1),(1,1,-1),
           (0x7fffffff,0x7fffffff,1),(-0x80000000,1,1),
           (0x10000,0x10000,0x10000),(1,1,0)]
    rng=random.Random(0x524606)
    cases += [(rng.randrange(-0x80000000,0x80000000),
               rng.randrange(-0x80000000,0x80000000),
               rng.randrange(-0x80000000,0x80000000)) for _ in range(128)]
    for address,name,arity in ((0x524606,'audio_uart_font_mul_div',3),
                                (0x524754,'audio_uart_font_divide_metric',2)):
        fn=getattr(lib,name)
        fn.argtypes=[ctypes.c_int32]*arity;fn.restype=ctypes.c_int32
        for triple in cases:
            args=triple[:arity]
            actual=stock(address,args)
            expected=fn(*args)
            assert actual==expected,(name,args,actual,expected)
        print(f'PASS {len(cases)}/{len(cases)} {name} original-byte/compiled-C')
