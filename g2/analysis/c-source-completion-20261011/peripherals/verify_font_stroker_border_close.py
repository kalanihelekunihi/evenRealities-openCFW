"""Bounded stock/C angle normalization and border close mutations."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'close.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_border_close',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_border_close.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    def machine():
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        return u
    def angle(compiled,a,b):
        u=machine();u.reg_write(UC_ARM_REG_R0,a&0xffffffff);u.reg_write(UC_ARM_REG_R1,b&0xffffffff)
        u.emu_start((symbols['audio_uart_font_stroker_angle_diff'] if compiled else 0x52910e)|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0)
    rng=random.Random(0x52910e)
    angles=[(-100,100),(0,0),(0,0x1680000),(0,-0x1680000),(0,0xb40000),(0,-0xb40000)]
    angles.extend((rng.randint(-0x2000000,0x2000000),rng.randint(-0x2000000,0x2000000)) for _ in range(30))
    for a,b in angles:
        x=angle(False,a,b);y=angle(True,a,b);assert x==y,(a,b,x,y)
    print('PASS angle',len(angles))
    def border(compiled,count,start,reverse):
        u=machine();B=0x20010000;P=0x20010100;T=0x20010200
        u.mem_write(B,struct.pack('<IIIIII',count,0,P,T,1,start))
        u.mem_write(P,b''.join(struct.pack('<ii',i*11,i*13) for i in range(8)))
        u.mem_write(T,bytes(range(8)))
        u.reg_write(UC_ARM_REG_R0,B);u.reg_write(UC_ARM_REG_R1,reverse)
        u.emu_start((symbols['audio_uart_font_stroker_border_close'] if compiled else 0x56834a)|1,0x600000,count=10000)
        return bytes(u.mem_read(B,24)),bytes(u.mem_read(P,64)),bytes(u.mem_read(T,8))
    cases=[(1,0,0),(2,0,0),(3,0,0),(4,0,0),(5,1,0),(5,1,1),(6,0,1),(7,1,1)]
    for case in cases:
        a=border(False,*case);b=border(True,*case);assert a==b,(case,a,b)
    print('PASS border',len(cases))
