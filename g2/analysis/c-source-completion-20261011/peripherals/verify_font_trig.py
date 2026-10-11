"""Compiled-C/stock vector-unit, cosine and sine with real CORDIC child."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    src=ROOT/'components/audio/uart_thread_source_candidate';elf=Path(d)/'trig.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_unit',str(src/'display_font_freetype_trig.c'),str(src/'display_font_freetype_cordic.c'),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    V=0x20010000
    def run(compiled,kind,angle):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(V,b'\0'*8)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if kind=='unit':u.reg_write(UC_ARM_REG_R0,V);u.reg_write(UC_ARM_REG_R1,angle&0xffffffff);addr=0x528fde;sym='audio_uart_font_vector_unit'
        elif kind=='cos':u.reg_write(UC_ARM_REG_R0,angle&0xffffffff);addr=0x528f8c;sym='audio_uart_font_vector_cos'
        else:u.reg_write(UC_ARM_REG_R0,angle&0xffffffff);addr=0x528f9a;sym='audio_uart_font_vector_sin'
        u.emu_start((syms[sym] if compiled else addr)|1,0x600000,count=20000)
        return struct.unpack('<ii',u.mem_read(V,8)) if kind=='unit' else u.reg_read(UC_ARM_REG_R0)
    rng=random.Random(0x528fde)
    cases=[-0xb40000,-0x5a0000,-1,0,1,0x2d0000,0x5a0000,0xb40000]+[rng.randint(-0x1680000,0x1680000) for _ in range(60)]
    for kind in ('unit','cos','sin'):
        for i,angle in enumerate(cases):
            a=run(False,kind,angle);b=run(True,kind,angle);assert a==b,(kind,i,angle,a,b)
        print('PASS trig',kind,len(cases))
