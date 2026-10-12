"""Actual ARM C/native rectangle setter and four-word-copy comparisons."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_layout_rect_primitives.c'
CASES=[(0x450b6c,'audio_uart_lv_rect_set_width_450b6c'),
       (0x450b76,'audio_uart_lv_rect_set_height_450b76'),
       (0x48b8f8,'audio_uart_lv_flex_rect_copy_48b8f8'),
       (0x48c7fc,'audio_uart_lv_grid_box_copy_48c7fc')]
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'primitives.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_rect_set_width_450b6c',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 total=0
 for native,name in CASES:
  for value in (0,1,11,0xffffffff):
   out=[]
   for is_c in (False,True):
    u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
    u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
    for a,d in segs:u.mem_write(a,d)
    dst,src=0x20003000,0x20003100
    u.mem_write(dst,struct.pack('<IIII',10,20,13,22));u.mem_write(src,struct.pack('<IIII',value,0x77,0x88,0x99))
    u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
    u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,src if native in (0x48b8f8,0x48c7fc) else value)
    u.emu_start((syms[name] if is_c else native)|1,0x600000,count=30)
    out.append(bytes(u.mem_read(dst,16)))
   assert out[0]==out[1],(name,value,out)
   total+=1
 print(f'PASS {total} compiled-C/native LV rectangle primitive cases')
