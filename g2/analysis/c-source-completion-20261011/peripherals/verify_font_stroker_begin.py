"""Stock/compiled C FT_Stroker_BeginSubPath state transition."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'begin.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_stroker_begin',str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_stroker_begin.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    STROKER=0x20010000;POINT=0x20010100
    def run(compiled,open_,cap,join,valid=True):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000);u.mem_write(STROKER,b'\xaa'*0x80)
        u.mem_write(STROKER+41,bytes([cap,join]));u.mem_write(POINT,struct.pack('<ii',-12345,6789))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,STROKER if valid else 0);u.reg_write(UC_ARM_REG_R1,POINT);u.reg_write(UC_ARM_REG_R2,open_)
        u.emu_start((symbols['audio_uart_font_stroker_begin'] if compiled else 0x5694e0)|1,0x600000,count=2000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(STROKER,0x50))
    for open_ in (0,1):
      for cap in (0,1):
       for join in (0,1):
        a=run(False,open_,cap,join);b=run(True,open_,cap,join);assert a==b,(open_,cap,join,a,b)
    assert run(False,0,0,0,False)==run(True,0,0,0,False)
    print('PASS begin 9/9')
