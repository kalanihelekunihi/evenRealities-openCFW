#!/usr/bin/env python3
"""Compare parser's no-header and 0x5a bad-CRC early returns."""
from pathlib import Path
import subprocess,itertools
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/record_scan_prefix_candidate.c'
obj=HERE/'record_scan_prefix_candidate.o';elf=HERE/'record_scan_prefix_candidate.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-c',str(SRC),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for offset,length in itertools.product((-1,0,1,2,3),(1,4,8)):
 input_bytes=bytearray([0x11]*64)
 if offset>=0:
  input_bytes[offset:offset+4]=bytes([0x5a,0xa5,0xff,length])
  input_bytes[offset+4]=0x5a
  input_bytes[offset+4+length]=0x00 # deliberately not the calculated CRC
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW)
  u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000)
  u.mem_write(0x20000664,bytes(input_bytes));u.mem_write(0x200000bf,b'\x01')
  u.reg_write(UC_ARM_REG_R0,0 if original else 0x20007000)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x08001e94 if original else sym['case_record_scan_prefix'])|1,0x20001000,count=20000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000
  pair.append(u.reg_read(UC_ARM_REG_R0))
 assert pair[0]==0xff and pair[1]==(0 if offset<0 else 2),(offset,length,pair)
 checked+=1
print('PASS_CASE_RECORD_PREFIX_EARLY',checked)
