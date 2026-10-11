"""Stock/compiled-C CORDIC core vector/angle fixtures."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'cordic.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_rotate_core',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_cordic.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    V=0x20010000
    def run(compiled,xy,angle):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(V,struct.pack('<ii',*xy))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,V);u.reg_write(UC_ARM_REG_R1,angle&0xffffffff)
        u.emu_start((symbols['audio_uart_font_vector_rotate_core'] if compiled else 0x528e5a)|1,0x600000,count=10000)
        return bytes(u.mem_read(V,8))
    rng=random.Random(0x528e5a)
    cases=[((0x10000000,0),0),((0x10000000,0),0x5a0000),((0x10000000,0),-0x5a0000),((0x12345678,-0x1020304),0x2d0000),((1,2),-0x2d0000)]
    cases.extend(((rng.randint(-0x20000000,0x20000000),rng.randint(-0x20000000,0x20000000)),rng.randint(-0xb40000,0xb40000)) for _ in range(70))
    for xy,angle in cases:
        a=run(False,xy,angle);b=run(True,xy,angle)
        assert a==b,(xy,angle,a.hex(),b.hex())
    print('PASS CORDIC',len(cases))
