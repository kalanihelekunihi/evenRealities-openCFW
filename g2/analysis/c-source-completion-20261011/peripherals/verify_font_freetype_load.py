"""Bounded stock/compiled-C FT_Load_Glyph driver path with controlled methods."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
LOWERS={'audio_uart_font_glyphslot_clear':0x5252bc,'audio_uart_font_get_format':0x524b64,
'audio_uart_font_outline_check':0x52798c,'audio_uart_font_grid_fit_metrics':0x5254c8,
'audio_uart_font_mul_div':0x524606,'audio_uart_font_slot_renderer':0x527096,
'audio_uart_font_outline_transform':0x527ba0,'audio_uart_font_outline_translate':0x527b2e,
'audio_uart_font_vector_transform':0x527b60,'audio_uart_font_render_glyph':0x527228,
'audio_uart_font_preset_bitmap':0x5250de}
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'load.elf'
    command=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_load_glyph']
    command += [f'-Wl,--defsym,{name}={hex(addr)}' for name,addr in LOWERS.items()]
    command += [str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_load_glyph.c'),'-o',str(elf)]
    subprocess.run(command,check=True,stderr=subprocess.DEVNULL)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    FACE=0x20010000;SLOT=0x20010200;DRIVER=0x20010300;LIBRARY=0x20010400
    DRIVER_CLASS=0x20010500;INTERNAL=0x20010600;SIZE=0x20010700;MODULE=0x20010800
    CALLBACK=0x20012000
    def put32(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
    def setup(u):
        for o,v in {0x54:SLOT,0x58:SIZE,0x60:DRIVER,0x80:INTERNAL}.items():put32(u,FACE+o,v)
        put32(u,DRIVER,MODULE);put32(u,DRIVER+4,LIBRARY);put32(u,DRIVER+0xc,DRIVER_CLASS)
        put32(u,DRIVER_CLASS+0x48,CALLBACK|1)
        put32(u,LIBRARY+0xa0,0);put32(u,MODULE,0)
        u.mem_write(CALLBACK,b'\x70\x47')
    def run(compiled,flags,face_valid):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);setup(u)
        calls=[]
        def intercept(uc,address,size,user):
            if address==0x5252bc:
                calls.append(('clear',uc.reg_read(UC_ARM_REG_R0)))
                uc.mem_write(SLOT,b'\0'*0x100)
            elif address==CALLBACK:
                args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
                calls.append(('load',args))
                put32(uc,SLOT+0x28,0x400);put32(uc,SLOT+0x34,0x500)
                put32(uc,SLOT+0x48,0x62697473)
            else:return
            uc.reg_write(UC_ARM_REG_R0,0)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,intercept)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,FACE if face_valid else 0)
        u.reg_write(UC_ARM_REG_R1,3);u.reg_write(UC_ARM_REG_R2,flags)
        address=symbols['audio_uart_font_load_glyph'] if compiled else 0x525574
        u.emu_start(address|1,0x600000,count=30000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(SLOT,0x80)),calls
    for flags,valid in [(0x208000,True),(0x108004,True),(0x208010,True),(0,False)]:
        a=run(False,flags,valid);b=run(True,flags,valid)
        assert a==b,(hex(flags),valid,a,b)
        print('PASS',hex(flags),valid)
