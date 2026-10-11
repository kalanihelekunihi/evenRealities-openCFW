#!/usr/bin/env python3
"""Original-byte comparison of stock 0x3a30 state preparation."""
from pathlib import Path
import subprocess,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
SRC=ROOT/'g2/components/case/startup_candidate_20261011/owned_lower_aliases_candidate.c'
obj=HERE/'owned_lower_aliases_oracle.o';elf=HERE/'owned_lower_aliases_oracle.elf'
subprocess.run(['/usr/bin/clang','--target=arm-none-eabi','-mcpu=cortex-m0plus','-mthumb','-Os','-ffreestanding','-fno-builtin','-ffunction-sections','-c',str(SRC),'-o',str(obj)],check=True)
subprocess.run(['/opt/homebrew/bin/arm-none-eabi-ld','--gc-sections','-e','case_init_sensor_prepare','--unresolved-symbols=ignore-all','-Ttext=0x00100000',str(obj),'-o',str(elf)],check=True,stderr=subprocess.DEVNULL)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for seed in range(8):
 raw=random.Random(seed).randbytes(0x100);pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20000880,raw)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x08003a30 if original else sym['case_init_sensor_prepare'])|1,0x20001000,count=5000)
  pair.append(bytes(u.mem_read(0x20000880,0x100)))
 assert pair[0]==pair[1],seed
print('PASS_CASE_SENSOR_PREPARE',8)
