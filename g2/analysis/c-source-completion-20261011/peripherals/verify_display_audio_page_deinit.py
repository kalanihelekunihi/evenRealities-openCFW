"""Actual compiled ARM C/native display audio page clear and deinit effects."""
from pathlib import Path
import subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_audio_page_deinit.c'
MEM=ROOT/'components/audio/uart_thread_source_candidate/freestanding_memory.c'
with tempfile.TemporaryDirectory() as td:
    elf=Path(td)/'test.elf'
    subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-ffreestanding',
                    '-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_display_page_deinit',
                    str(SRC),str(MEM),'-o',str(elf)],check=True)
    syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
    with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
    for label,native,c_name in (('clear',0x45fb7c,'audio_uart_display_page_clear_45fb7c'),
                                ('deinit',0x45fbae,'audio_uart_display_page_deinit')):
        for null in (False,True):
            traces=[]
            for is_c in (False,True):
                u=Uc(UC_ARCH_ARM,UC_MODE_THUMB)
                u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
                u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
                for a,d in segs:u.mem_write(a,d)
                obj=0x20001000;u.mem_write(obj,b'\xa5'*0xd0)
                u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
                u.reg_write(UC_ARM_REG_R0,0 if null else obj)
                u.emu_start((syms[c_name] if is_c else native)|1,0x600000,count=2000)
                traces.append(bytes(u.mem_read(obj,0xd0)))
            assert traces[0]==traces[1],(label,null)
    print('PASS 4 compiled-C/native page clear/deinit memory cases')
