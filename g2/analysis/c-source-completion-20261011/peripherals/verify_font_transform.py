"""Stock versus compiled C FT_MulFix/vector/outline transform."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'transform.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_outline_transform',
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_transform.c'),str(ROOT/'components/audio/uart_thread_source_candidate/display_font_metric_scale.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    def run(compiled,kind,pts,matrix):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        outline=0x20010000;points=0x20010100;mat=0x20010200
        u.mem_write(outline,struct.pack('<hhIIII',1,len(pts),points,0,0,0))
        u.mem_write(points,b''.join(struct.pack('<ii',*p) for p in pts))
        u.mem_write(mat,struct.pack('<iiii',*matrix))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,outline if kind=='outline' else points)
        u.reg_write(UC_ARM_REG_R1,mat)
        addr=(symbols['audio_uart_font_outline_transform'] if kind=='outline' else symbols['audio_uart_font_vector_transform']) if compiled else (0x527ba0 if kind=='outline' else 0x527b60)
        u.emu_start(addr|1,0x600000,count=10000)
        return bytes(u.mem_read(points,len(pts)*8))
    rng=random.Random(0x527ba0)
    cases=[([(1,2)],(65536,0,0,65536)),([(-200000,100000)],(32768,-32768,131072,65536)),([(0,0),(100,200),(-12,600)],(60000,12000,-10000,70000))]
    cases.extend(([(rng.randint(-2**20,2**20),rng.randint(-2**20,2**20)) for _ in range(3)],tuple(rng.randint(-2**17,2**17) for _ in range(4))) for _ in range(20))
    for kind in ('vector','outline'):
        for i,(pts,matrix) in enumerate(cases):
            a=run(False,kind,pts,matrix);b=run(True,kind,pts,matrix)
            assert a==b,(kind,i,pts,matrix,a.hex(),b.hex())
        print('PASS',kind,len(cases))
