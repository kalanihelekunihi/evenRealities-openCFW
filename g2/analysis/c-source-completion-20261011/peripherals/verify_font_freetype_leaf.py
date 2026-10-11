"""Controlled stock-byte versus compiled-C FreeType index/get/done leaves."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'leaf.elf'
    src=ROOT/'components/audio/uart_thread_source_candidate'
    command=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_get_glyph',
      '-Wl,--defsym,audio_uart_font_bitmap_glyph_class=0x7601b0',
      '-Wl,--defsym,audio_uart_font_outline_glyph_class=0x7601d0',
      '-Wl,--defsym,audio_uart_font_lookup_renderer=0x52705a',
      '-Wl,--defsym,audio_uart_buffer_zero=0x43c0e4',
      str(src/'display_font_freetype_glyph_leaf.c'),str(src/'display_font_freetype_get_glyph.c'),'-o',str(elf)]
    subprocess.run(command,check=True,stderr=subprocess.DEVNULL)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    FACE=0x20010000;CHARMAP=0x20010100;CHARCLASS=0x20010200;SLOT=0x20010300
    LIBRARY=0x20010400;MEMORY=0x20010500;GLYPH=0x20010600;OUT=0x20010700
    CHARMAP_CALLBACK=0x20012000;ALLOC_CALLBACK=0x20012020;FREE_CALLBACK=0x20012040
    CALLBACKS={CHARMAP_CALLBACK:'charmap',ALLOC_CALLBACK:'allocate',FREE_CALLBACK:'free',
               0x567ca0:'bitmap_init',0x43c0e4:'zero'}
    def put32(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
    def setup(u):
        put32(u,FACE+0x5c,CHARMAP);put32(u,FACE+0x10,10)
        put32(u,CHARMAP+0xc,CHARCLASS);put32(u,CHARCLASS+0xc,CHARMAP_CALLBACK|1)
        put32(u,SLOT,LIBRARY);put32(u,SLOT+0x40,64);put32(u,SLOT+0x44,128)
        put32(u,SLOT+0x48,0x62697473)
        put32(u,LIBRARY,MEMORY);put32(u,MEMORY+4,ALLOC_CALLBACK|1);put32(u,MEMORY+8,FREE_CALLBACK|1)
        for a in (CHARMAP_CALLBACK,ALLOC_CALLBACK,FREE_CALLBACK):u.mem_write(a,b'\x70\x47')
    def run(compiled,kind,value):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);setup(u)
        calls=[]
        def intercept(uc,address,size,user):
            name=CALLBACKS.get(address)
            if name is None:return
            r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1)
            calls.append((name,r0,r1))
            result=0
            if name=='charmap':result=value
            elif name=='allocate':result=GLYPH
            elif name=='zero':uc.mem_write(r0,b'\0'*r1)
            uc.reg_write(UC_ARM_REG_R0,result)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,intercept)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        if kind=='index':
            u.reg_write(UC_ARM_REG_R0,FACE);u.reg_write(UC_ARM_REG_R1,65)
            address=symbols['audio_uart_font_get_char_index'] if compiled else 0x526f10
        elif kind=='get':
            u.reg_write(UC_ARM_REG_R0,SLOT);u.reg_write(UC_ARM_REG_R1,OUT)
            address=symbols['audio_uart_font_get_glyph'] if compiled else 0x567ec8
        else:
            put32(u,GLYPH,LIBRARY);put32(u,GLYPH+4,0x7601b0)
            u.reg_write(UC_ARM_REG_R0,GLYPH)
            address=symbols['audio_uart_font_done_glyph'] if compiled else 0x567f88
        u.emu_start(address|1,0x600000,count=30000)
        result=u.reg_read(UC_ARM_REG_R0) if kind!='done' else 0
        return result,bytes(u.mem_read(OUT,4)),bytes(u.mem_read(GLYPH,0x20)),calls
    for kind,value in [('index',5),('index',10),('get',0),('done',0)]:
        a=run(False,kind,value);b=run(True,kind,value)
        if kind=='done':
            a=a[:3]+(tuple(x[0] for x in a[3]),);b=b[:3]+(tuple(x[0] for x in b[3]),)
        assert a==b,(kind,value,a,b)
        print('PASS',kind,value)
