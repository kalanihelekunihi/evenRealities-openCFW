"""Stock/compiled C CORDIC scale and shrink over signed boundaries."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'scalars.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_normalize',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_rotate_scalars.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    def machine():
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        return u
    def normalize(compiled,xy):
        u=machine();addr=0x20010000;u.mem_write(addr,struct.pack('<ii',*xy));u.reg_write(UC_ARM_REG_R0,addr)
        u.emu_start((symbols['audio_uart_font_vector_normalize'] if compiled else 0x528e18)|1,0x600000,count=5000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(addr,8))
    def shrink(compiled,x):
        u=machine();u.reg_write(UC_ARM_REG_R0,x&0xffffffff)
        u.emu_start((symbols['audio_uart_font_vector_shrink'] if compiled else 0x528db8)|1,0x600000,count=5000)
        return u.reg_read(UC_ARM_REG_R0)
    rng=random.Random(0x528db8)
    vals=[0,1,-1,2,-2,0x7fffffff,-0x80000000,0x40000000,-0x40000000,123456,-789123]
    vals.extend(rng.randint(-0x80000000,0x7fffffff) for _ in range(90))
    for x in vals:
        a=shrink(False,x);b=shrink(True,x);assert a==b,(x,a,b)
    print('PASS shrink',len(vals))
    pairs=[(0,0),(1,0),(-1,-1),(0x7fffffff,0),(-0x80000000,1)]
    pairs.extend((rng.choice(vals),rng.choice(vals)) for _ in range(60))
    for xy in pairs:
        a=normalize(False,xy);b=normalize(True,xy);assert a==b,(xy,a,b)
    print('PASS normalize',len(pairs))
