"""Actual compiled-C/native LV flex placement full small enum/count matrix."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_flex_place.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'test.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib','-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_place_content_48c6d8',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 for place in range(7):
  for count in range(4):
   outs=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    start=0x20003000;gap=0x20003004
    u.mem_write(start,struct.pack('<ii',10,5))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    for reg,val in ((UC_ARM_REG_R0,place),(UC_ARM_REG_R1,101),(UC_ARM_REG_R2,26),(UC_ARM_REG_R3,count)):
     u.reg_write(reg,val)
    u.mem_write(0x200ff000,struct.pack('<II',start,gap))
    u.emu_start((syms['audio_uart_lv_place_content_48c6d8'] if is_c else 0x48c6d8)|1,0x600000,count=90)
    outs.append(bytes(u.mem_read(start,8)))
   assert outs[0]==outs[1],(place,count,outs)
 print('PASS 28 compiled-C/native LV flex placement cases')
