"""Bounded stock versus compiled-C outline check/copy/translate."""
from pathlib import Path
import subprocess,tempfile,struct
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_LR,UC_ARM_REG_SP
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
with tempfile.TemporaryDirectory() as d:
    elf=Path(d)/'storage.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
      '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_font_outline_check',
      str(ROOT/'components/audio/uart_thread_source_candidate/display_font_freetype_outline_storage.c'),
      str(ROOT/'components/audio/uart_thread_source_candidate/byte_copy.c'),'-o',str(elf)],check=True)
    symbols=dict((p[2],int(p[0],16)) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(p:=line.split())==3)
    with elf.open('rb') as f:
        e=ELFFile(f);segments=[(seg['p_vaddr'],seg.data()) for seg in e.iter_segments() if seg['p_type']=='PT_LOAD']
    BASE=0x20010000;TARGET=0x20010080;POINTS=0x20010100;TAGS=0x20010200;ENDS=0x20010300
    TARGET_POINTS=0x20010400;TARGET_TAGS=0x20010500;TARGET_ENDS=0x20010600
    stock={'check':0x52798c,'copy':0x5279e0,'translate':0x527b2e}
    candidate={'check':'audio_uart_font_outline_check','copy':'audio_uart_font_outline_copy','translate':'audio_uart_font_outline_translate'}
    def run(compiled,kind,ends=(2,),target_counts=None):
        u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
        u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
        u.mem_map(0x100000,0x100000)
        for v,data in segments:u.mem_write(v,data)
        u.mem_map(0x20000000,0x100000)
        point_count=3;contour_count=len(ends)
        u.mem_write(BASE,struct.pack('<hhIIII',contour_count,point_count,POINTS,TAGS,ENDS,0x55))
        tc,tp=target_counts or (contour_count,point_count)
        u.mem_write(TARGET,struct.pack('<hhIIII',tc,tp,TARGET_POINTS,TARGET_TAGS,TARGET_ENDS,0x22))
        u.mem_write(POINTS,struct.pack('<iiiiii',1,-2,3,4,5,6))
        u.mem_write(TAGS,b'\x01\x00\x01')
        u.mem_write(ENDS,struct.pack('<'+'h'*len(ends),*ends))
        u.mem_write(TARGET_POINTS,b'\xaa'*24);u.mem_write(TARGET_TAGS,b'\xaa'*3);u.mem_write(TARGET_ENDS,b'\xaa'*max(2,len(ends)*2))
        u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
        u.reg_write(UC_ARM_REG_R0,BASE)
        u.reg_write(UC_ARM_REG_R1,TARGET if kind=='copy' else 10)
        u.reg_write(UC_ARM_REG_R2,(-20)&0xffffffff)
        addr=symbols[candidate[kind]] if compiled else stock[kind]
        u.emu_start(addr|1,0x600000,count=10000)
        if kind=='check':return u.reg_read(UC_ARM_REG_R0)
        if kind=='copy':return u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(TARGET,20)),bytes(u.mem_read(TARGET_POINTS,24)),bytes(u.mem_read(TARGET_TAGS,3)),bytes(u.mem_read(TARGET_ENDS,max(2,len(ends)*2)))
        return bytes(u.mem_read(POINTS,24))
    cases=[('check',(2,),None),('check',(1,),None),('check',(0,2),None),('check',(2,2),None),('copy',(2,),None),('copy',(2,),(1,2)),('translate',(2,),None)]
    for kind,ends,target_counts in cases:
        a=run(False,kind,ends,target_counts);b=run(True,kind,ends,target_counts)
        assert a==b,(kind,ends,target_counts,a,b)
        print('PASS',kind,ends,target_counts)
