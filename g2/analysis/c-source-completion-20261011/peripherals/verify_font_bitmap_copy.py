"""Actual compiled-C/stock FT_Bitmap_Copy bounded no-allocation comparisons."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=0x20010000;DST=0x20010100;LIB=0x20010200;SB=0x20011000;DB=0x20012000
with tempfile.TemporaryDirectory() as td:
    shim=Path(td)/'alloc.c';shim.write_text('void *audio_uart_font_mem_alloc(void *m,int n,int *e){(void)m;(void)n;*e=64;return 0;}\nvoid *audio_uart_font_mem_realloc_raw(void *m,int i,int o,int n,void *p,int *e){(void)m;(void)i;(void)o;(void)n;(void)p;*e=64;return 0;}\n')
    elf=Path(td)/'copy.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_bitmap_copy',*(str(ROOT/'components/audio/uart_thread_source_candidate'/f) for f in ['display_font_freetype_bitmap_copy.c','byte_copy.c']),str(shim),'-o',str(elf)],check=True)
    sym=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f: segments=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    def run(candidate,kind,srcpitch,dstpitch):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB);u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        u.mem_write(LIB,struct.pack('<I',0x20015000));u.mem_write(SB,bytes(range(1,17)));u.mem_write(DB,b'Z'*16)
        sbody=struct.pack('<IiiIII',2,4,srcpitch,0 if kind=='empty' else SB,1,2)
        dbody=struct.pack('<IiiIII',2,4,dstpitch,DB,7,8)
        u.mem_write(SRC,sbody);u.mem_write(DST,dbody)
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,LIB if kind!='nolib' else 0)
        u.reg_write(UC_ARM_REG_R1,SRC if kind!='nosrc' else 0)
        u.reg_write(UC_ARM_REG_R2,SRC if kind=='same' else DST)
        u.emu_start((sym['audio_uart_font_bitmap_copy'] if candidate else 0x58ed2e)|1,0x600000,count=20000)
        return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(DST,24)),bytes(u.mem_read(DB,16))
    cases=[('nolib',4,4),('nosrc',4,4),('same',4,4),('empty',4,4),('empty',-4,4),('copy',4,4),('copy',4,-4),('copy',-4,4)]
    for case in cases:
        stock=run(False,*case);source=run(True,*case)
        assert stock==source,(case,stock,source)
        print('PASS bitmap copy',case)
