"""Actual ARM C/native grid descriptor count and signed weighted rounding."""
from pathlib import Path
import struct,subprocess,tempfile
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB
from unicorn.arm_const import *
ROOT=Path(__file__).resolve().parents[3]
BLOB=(ROOT/'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
SRC=ROOT/'components/audio/uart_thread_source_candidate/display_lv_grid_descriptor_helpers.c'
with tempfile.TemporaryDirectory() as td:
 elf=Path(td)/'grid.elf'
 subprocess.run(['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-O2','-nostdlib',
                 '-Wl,-Ttext=0x100000','-Wl,-e,audio_uart_lv_grid_descriptor_count_48d4d0',str(SRC),'-o',str(elf)],check=True)
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True).splitlines() if len(v:=line.split())==3}
 with elf.open('rb') as f:segs=[(s['p_vaddr'],s.data()) for s in ELFFile(f).iter_segments() if s['p_type']=='PT_LOAD']
 cases=[(0x48d4d0,'audio_uart_lv_grid_descriptor_count_48d4d0',n,0) for n in range(5)]
 cases += [(0x48ca18,'audio_uart_lv_grid_weight_round_48ca18',n,d) for n in (-37,-1,0,1,37) for d in (1,2,3,7)]
 for native,name,p0,p1 in cases:
  outs=[]
  for is_c in (False,True):
   u=Uc(UC_ARCH_ARM,UC_MODE_THUMB);u.mem_map(0x400000,0x400000);u.mem_write(0x438000,BLOB)
   u.mem_map(0x100000,0x100000);u.mem_map(0x20000000,0x100000)
   for a,d in segs:u.mem_write(a,d)
   u.mem_write(0x20003000,struct.pack('<'+'I'*(p0+1),*([11]*p0+[0x1fffffff])) if native==0x48d4d0 else b'\0'*24)
   u.reg_write(UC_ARM_REG_SP,0x200ff000);u.reg_write(UC_ARM_REG_LR,0x600001)
   u.reg_write(UC_ARM_REG_R0,0x20003000 if native==0x48d4d0 else p0&0xffffffff)
   u.reg_write(UC_ARM_REG_R1,p1)
   u.emu_start((syms[name] if is_c else native)|1,0x600000,count=100)
   outs.append(u.reg_read(UC_ARM_REG_R0))
  assert outs[0]==outs[1],(name,p0,p1,outs)
 print(f'PASS {len(cases)} compiled-C/native LV grid descriptor helper cases')
