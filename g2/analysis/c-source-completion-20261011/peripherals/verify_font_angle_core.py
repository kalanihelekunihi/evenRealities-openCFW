"""Bounded actual C/stock CORDIC angle-core arithmetic."""
from pathlib import Path
import subprocess,tempfile,struct,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3];BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'core.elf';subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_vector_angle_core',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_angle_core.c'),'-o',str(elf)],check=True)
    syms=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:e=ELFFile(f);segs=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
    V=0x20010000
    def run(compiled,x,y):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segs:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(V,struct.pack('<ii',x,y))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001);u.reg_write(UC_ARM_REG_R0,V)
        u.emu_start((syms['audio_uart_font_vector_angle_core'] if compiled else 0x528ee4)|1,0x600000,count=20000)
        return struct.unpack('<ii',u.mem_read(V,8))
    rng=random.Random(0x528ee4)
    cases=[(x,y) for x in (-0x30000000,-0x10000000,-1,0,1,0x10000000,0x30000000) for y in (-0x30000000,-0x10000000,-1,0,1,0x10000000,0x30000000)]
    cases += [(rng.randint(-0x3fffffff,0x3fffffff),rng.randint(-0x3fffffff,0x3fffffff)) for _ in range(80)]
    for i,(x,y) in enumerate(cases):
        a=run(False,x,y);b=run(True,x,y);assert a==b,(i,x,y,a,b)
    print('PASS angle core',len(cases),'actual C/stock vectors')
