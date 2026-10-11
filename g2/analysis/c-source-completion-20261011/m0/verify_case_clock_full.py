#!/usr/bin/env python3
"""Full bounded original/source clock-plan cases that avoid priority child."""
from pathlib import Path
import subprocess,itertools,random
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
subprocess.run(['/tmp/iar-c-runtime-venv/bin/python',str(HERE/'verify_case_clock_prefix.py')],check=True,capture_output=True)
elf=HERE/'clock_prefix_oracle.elf'
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
checked=0
for plan,rate,prescale,seed,index in itertools.product((0,1,3,4,5),(0xf4240,0x3d0900),(0,0x1000),range(2),range(8)):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x40021000,0x1000);u.mem_map(0x40022000,0x1000);u.mem_map(0x40014000,0x1000);u.mem_map(0xe000e000,0x1000)
  u.mem_write(0x20000f4c,random.Random(seed).randbytes(0x60));u.mem_write(0x40014800,random.Random(seed+100).randbytes(0x40));u.mem_write(0x20000124,rate.to_bytes(4,'little'));u.mem_write(0x40021008,(prescale|(index<<12)).to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,plan);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x08004f14 if original else sym['case_transfer_clock_config'])|1,0x20001000,count=100000)
  pair.append((u.reg_read(UC_ARM_REG_PC),u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000f4c,0x60)),bytes(u.mem_read(0x40014800,0x40)),bytes(u.mem_read(0xe000e100,4)),bytes(u.mem_read(0xe000e414,4))))
 assert pair[0]==pair[1],(plan,rate,prescale,seed,index,[(hex(x[0]),x[1],x[2].hex(),x[3].hex(),x[4].hex(),x[5].hex()) for x in pair])
 checked+=1
print('PASS_CASE_CLOCK_FULL',checked)
