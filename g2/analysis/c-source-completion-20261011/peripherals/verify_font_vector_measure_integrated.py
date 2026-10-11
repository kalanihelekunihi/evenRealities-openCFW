"""Connected C vector angle/length arithmetic against original stock bodies."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    src=ROOT/'components/audio/uart_thread_source_candidate';elf=Path(d)/'measure.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_angle',str(src/'display_font_freetype_vector_measure.c'),str(src/'display_font_freetype_rotate_scalars.c'),str(src/'display_font_freetype_angle_core.c'),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    V=0x20010000
    def run(compiled,kind,x,y):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(V,struct.pack('<ii',x,y))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if kind=='angle':u.reg_write(UC_ARM_REG_R0,x&0xffffffff);u.reg_write(UC_ARM_REG_R1,y&0xffffffff);addr=0x528fbc;sym='audio_uart_font_vector_angle'
        else:u.reg_write(UC_ARM_REG_R0,V);addr=0x529086;sym='audio_uart_font_vector_length'
        u.emu_start((syms[sym] if compiled else addr)|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0)
    rng=random.Random(0x529086)
    cases=[(x,y) for x in (-100000,-1,0,1,100000) for y in (-100000,-1,0,1,100000)]
    cases += [(rng.randint(-0x3fffffff,0x3fffffff),rng.randint(-0x3fffffff,0x3fffffff)) for _ in range(80)]
    for kind in ('angle','length'):
        for i,(x,y) in enumerate(cases):
            a=run(False,kind,x,y);b=run(True,kind,x,y);assert a==b,(kind,i,x,y,a,b)
        print('PASS integrated measure',kind,len(cases))
