"""Bounded native/compiled-C outline renderer comparison with controlled lowers."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
LOWERS={'audio_uart_font_face_load_scalable':0x526d54,'audio_uart_font_load_glyph':0x525574,
 'audio_uart_font_embolden_outline':0x527bca,'audio_uart_font_decompose_outline':0x527508,
 'audio_uart_font_stroker_create':0x5687b6,'audio_uart_font_stroker_configure':0x5687fe,
 'audio_uart_font_stroker_destroy':0x568844,'audio_uart_font_get_glyph':0x567ec8,
 'audio_uart_font_stroke_glyph':0x569954,'audio_uart_font_outline_release':0x52a264,
 'audio_uart_font_outline_context':0x4b1fcc,'audio_uart_font_outline_dispatch':0x529ea2,
 'audio_uart_buffer_zero':0x529b2c,'audio_uart_checksum_copy':0x439c04,
 'audio_uart_lvgl_log':0x44d25c}
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'outline.elf'
    command=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_outline_render']
    command += [f'-Wl,--defsym,{name}={hex(addr)}' for name,addr in LOWERS.items()]
    command += [str(ROOT/'components/audio/uart_thread_source_candidate/display_font_outline_render.c'),'-o',str(elf)]
    subprocess.run(command,check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    CTX=0x20010000;FACE=0x20010100;SLOT=0x20010200;TAGS=0x20010300;OBJECT=0x20010400
    RETURN=0x600000
    def put32(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
    def run(compiled,failure,width):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        put32(u,FACE+0x54,SLOT)
        u.mem_write(SLOT+0x6c,struct.pack('<hhIIII',1,2,0,TAGS,0,0))
        u.mem_write(TAGS,b'\x01\x01')
        u.mem_write(0x20010614,struct.pack('<hhIIII',1,2,0,TAGS,0,0))
        calls=[]
        targets={addr:name for name,addr in LOWERS.items()}
        def intercept(uc,address,size,user):
            name=targets.get(address)
            if name is None:return
            args=tuple(uc.reg_read(r) for r in (UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3))
            if name in {'audio_uart_font_face_load_scalable','audio_uart_font_load_glyph',
                        'audio_uart_font_decompose_outline','audio_uart_font_outline_dispatch'}:
                if name=='audio_uart_font_outline_dispatch':
                    packet=bytes(uc.mem_read(args[2],40))
                    calls.append((name,args[0],args[1],
                                  struct.unpack_from('<II',packet,32) if args[1]==40 else
                                  (struct.unpack_from('<I',packet,0)[0],packet[4])))
                elif name=='audio_uart_font_decompose_outline':
                    outline=bytes(uc.mem_read(args[0],20))
                    calls.append((name,struct.unpack_from('<hh',outline,0),args[2]))
                else:calls.append((name,args[:3]))
            value=0x17 if failure==name else 0
            if name=='audio_uart_font_stroker_create':uc.mem_write(args[1],struct.pack('<I',0x20010500))
            if name=='audio_uart_font_get_glyph':uc.mem_write(args[1],struct.pack('<I',0x20010600))
            if name=='audio_uart_font_outline_dispatch':
                value=1
                if args[1]==0x28:uc.mem_write(args[2],struct.pack('<I',OBJECT))
            elif name=='audio_uart_font_outline_context':value=CTX
            elif name=='audio_uart_buffer_zero':uc.mem_write(args[0],b'\0'*args[1])
            elif name=='audio_uart_checksum_copy':uc.mem_write(args[0],bytes(uc.mem_read(args[1],args[2])))
            uc.reg_write(UC_ARM_REG_R0,value)
            uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
        u.hook_add(UC_HOOK_CODE,intercept)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,RETURN|1)
        u.reg_write(UC_ARM_REG_R0,CTX);u.reg_write(UC_ARM_REG_R1,FACE)
        u.reg_write(UC_ARM_REG_R2,3);u.reg_write(UC_ARM_REG_R3,12)
        put32(u,0x200ff000,0);put32(u,0x200ff004,width)
        address=symbols['audio_uart_font_outline_render'] if compiled else 0x529f8e
        u.emu_start(address|1,RETURN,count=20000)
        return u.reg_read(UC_ARM_REG_R0),calls
    for failure,width in [('audio_uart_font_face_load_scalable',0),('audio_uart_font_load_glyph',0),(None,0),(None,2)]:
        a=run(False,failure,width);b=run(True,failure,width)
        assert a==b,(failure,width,a,b)
        print('PASS',failure,width)
