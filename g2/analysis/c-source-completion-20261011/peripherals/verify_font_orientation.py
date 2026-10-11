"""Stock/compiled C FT_Outline_Get_Orientation with controlled CBox."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_LR,UC_ARM_REG_PC,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'orientation.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_outline_orientation',
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_orientation.c'),
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_cbox.c'),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    OUTLINE=0x20010000;POINTS=0x20010100;CONTOURS=0x20010200
    def run(compiled,pts):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(OUTLINE,struct.pack('<hhIIII',1,len(pts),POINTS,0,CONTOURS,0))
        u.mem_write(POINTS,b''.join(struct.pack('<ii',*p) for p in pts))
        u.mem_write(CONTOURS,struct.pack('<h',len(pts)-1))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,OUTLINE)
        addr=symbols['audio_uart_font_outline_orientation'] if compiled else 0x527e0a
        u.emu_start(addr|1,0x600000,count=10000)
        return u.reg_read(UC_ARM_REG_R0)
    cases=[[(0,0),(100,0),(0,100)],[(0,0),(0,100),(100,0)],
           [(0,0),(100,0),(200,0)],[(-100,-100),(200,-50),(0,300)]]
    for pts in cases:
        a=run(False,pts);b=run(True,pts)
        assert a==b,(pts,a,b)
        print('PASS',a,pts)
