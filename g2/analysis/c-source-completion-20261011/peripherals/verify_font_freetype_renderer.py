"""Controlled stock/compiled-C renderer lookup and glyph render dispatch."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'renderer.elf';src=ROOT/'components/audio/uart_thread_source_candidate'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
       '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_render_glyph',
       str(src/'display_font_freetype_renderer.c'),str(src/'display_font_freetype_render_glyph.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    SLOT=0x20010000;FACE=0x20010100;DRIVER=0x20010200;LIB=0x20010300
    NODE=0x20010400;RENDERER=0x20010500;CALLBACK=0x20012000
    def put32(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
    def run(compiled,fmt,mode):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        put32(u,SLOT+4,FACE);put32(u,SLOT+0x48,fmt)
        put32(u,FACE+0x60,DRIVER);put32(u,DRIVER+4,LIB)
        put32(u,LIB+0x94,NODE);put32(u,LIB+0x9c,RENDERER)
        put32(u,NODE+8,RENDERER);put32(u,RENDERER+0x10,fmt)
        put32(u,RENDERER+0x3c,CALLBACK|1);u.mem_write(CALLBACK,b'\x70\x47')
        calls=[]
        def intercept(uc,address,size,user):
            if address!=CALLBACK:return
            calls.append(tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3)))
            uc.reg_write(UC_ARM_REG_R0,0)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,intercept)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,SLOT);u.reg_write(UC_ARM_REG_R1,mode)
        address=symbols['audio_uart_font_render_glyph'] if compiled else 0x527228
        u.emu_start(address|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),calls
    for fmt,mode in [(0x62697473,0),(0x6f75746c,0),(0x6f75746c,0x100),
                     (0x6f75746c,2),(0x12345678,1)]:
        a=run(False,fmt,mode);b=run(True,fmt,mode)
        assert a==b,(hex(fmt),mode,a,b)
        print('PASS',hex(fmt),mode)
