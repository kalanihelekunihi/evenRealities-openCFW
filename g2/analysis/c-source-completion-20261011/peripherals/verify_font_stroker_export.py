"""Stock/compiled-C border count and export, controlled closed/open tags."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'stroker.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_get_counts',
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_export.c'),
      str(ROOT/'components/audio/uart_thread_source_candidate/byte_copy.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    STROKER=0x20010000;BORDER=STROKER+0x34;POINTS=0x20010100;TAGS=0x20010200;OUTLINE=0x20010300
    OUT_POINTS=0x20010400;OUT_TAGS=0x20010500;OUT_ENDS=0x20010600;COUNTS=0x20010700
    def run(compiled,kind,tags):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(BORDER,struct.pack('<IIIIIII',len(tags),0,POINTS,TAGS,0,0,0)+b'\x01')
        u.mem_write(POINTS,b''.join(struct.pack('<ii',i*10,i*20) for i in range(len(tags))))
        u.mem_write(TAGS,bytes(tags));u.mem_write(COUNTS,b'\xaa'*8)
        u.mem_write(OUTLINE,struct.pack('<hhIIII',0,0,OUT_POINTS,OUT_TAGS,OUT_ENDS,0))
        u.mem_write(OUT_POINTS,b'\xaa'*64);u.mem_write(OUT_TAGS,b'\xaa'*8);u.mem_write(OUT_ENDS,b'\xaa'*16)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,STROKER);u.reg_write(UC_ARM_REG_R1,0)
        if kind=='count':
            u.reg_write(UC_ARM_REG_R2,COUNTS);u.reg_write(UC_ARM_REG_R3,COUNTS+4)
            addr=symbols['audio_uart_font_stroker_get_counts'] if compiled else 0x5696d4
        else:
            u.reg_write(UC_ARM_REG_R2,OUTLINE)
            addr=symbols['audio_uart_font_stroker_export'] if compiled else 0x569716
        u.emu_start(addr|1,0x600000,count=20000)
        if kind=='count':return bytes(u.mem_read(COUNTS,8)),bytes(u.mem_read(BORDER+28,1))
        return bytes(u.mem_read(OUTLINE,20)),bytes(u.mem_read(OUT_POINTS,64)),bytes(u.mem_read(OUT_TAGS,8)),bytes(u.mem_read(OUT_ENDS,16))
    cases=[('closed',[4|1,1,8|1]),('conic',[4|1,0,8|1]),('cubic',[4|1,2,2,8|1]),('open',[4|1,1]),('bad',[1,8|1])]
    for name,tags in cases:
        for kind in ('count','export'):
            a=run(False,kind,tags);b=run(True,kind,tags)
            assert a==b,(name,kind,a,b)
            print('PASS',name,kind)
