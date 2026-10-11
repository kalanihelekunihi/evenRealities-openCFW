"""End-to-end compiled C FT_Vector_From_Polar versus stock bytes."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]/'components/audio/uart_thread_source_candidate'
BLOB=(Path(__file__).resolve().parents[3]/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'polar.elf'
    files=['display_font_freetype_polar.c','display_font_freetype_rotate.c','display_font_freetype_rotate_scalars.c','display_font_freetype_cordic.c']
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_from_polar',*[str(ROOT/f) for f in files],'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    V=0x20010000
    def run(compiled,length,angle):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(V,b'\xaa'*8)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,V);u.reg_write(UC_ARM_REG_R1,length&0xffffffff);u.reg_write(UC_ARM_REG_R2,angle&0xffffffff)
        u.emu_start((symbols['audio_uart_font_vector_from_polar'] if compiled else 0x5290fa)|1,0x600000,count=10000)
        return bytes(u.mem_read(V,8))
    rng=random.Random(0x5290fa)
    cases=[(0,0),(1,0),(1000,0x2d0000),(333,0x5a0000),(0x10000,-0x5a0000)]
    cases.extend((rng.randint(1,0x1000000),rng.randint(-0xb40000,0xb40000)) for _ in range(50))
    for case in cases:
        a=run(False,*case);b=run(True,*case)
        assert a==b,(case,a.hex(),b.hex())
    print('PASS integrated polar',len(cases))
