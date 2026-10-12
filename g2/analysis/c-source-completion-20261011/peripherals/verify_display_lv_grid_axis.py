"""Actual ARM C/native LV grid axis matrix over placement, count and direction."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_grid_axis.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'axis.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_basic_axis_48d3c8',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 total=0
 for mode in range(7):
  for count in (1,2,3):
   for auto in (0,1):
    for reverse in (0,1):
     outs=[]
     for is_c in (False,True):
      u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
      u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
      for a,d in segs:u.mem_write(a,d)
      sizes,positions,sp=0x20003000,0x20003100,0x200ff000
      u.mem_write(sizes,struct.pack('<iii',10,20,30));u.mem_write(positions,struct.pack('<iii',7,7,7))
      u.mem_write(sp,struct.pack('<IIII',count,sizes,positions,reverse))
      u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x600001)
      for r,v in ((UC_ARM_REG_R0,100),(UC_ARM_REG_R1,auto),(UC_ARM_REG_R2,mode),(UC_ARM_REG_R3,5)):u.reg_write(r,v)
      u.emu_start((syms['audio_uart_lv_basic_axis_48d3c8'] if is_c else 0x48d3c8)|1,
                  0x600000,count=400)
      outs.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(positions,12))))
     assert outs[0]==outs[1],(mode,count,auto,reverse,outs)
     total+=1
 print(f'PASS {total} compiled-C/native LV grid axis cases')
