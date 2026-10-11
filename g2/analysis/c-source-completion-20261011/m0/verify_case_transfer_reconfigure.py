#!/usr/bin/env python3
"""Compare transfer reconfiguration through the 0x08004f14 child-call boundary."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
subprocess.run(['/tmp/iar-c-runtime-venv/bin/python',str(HERE/'verify_case_transfer_control.py')],check=True,capture_output=True)
elf=HERE/'transfer_control_candidate.oracle.elf'
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
for field16,field20 in ((0,0),(0x800,1),(0x1800,2)):
 cfg=bytearray(0x40);cfg[0]=2;cfg[16:20]=field16.to_bytes(4,'little');cfg[20:24]=field20.to_bytes(4,'little')
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20007000,bytes(cfg));u.mem_map(0x40021000,0x1000);u.mem_map(0x40007000,0x1000)
  u.reg_write(UC_ARM_REG_R0,0x20007000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  target=0x08004f14 if original else sym['case_transfer_clock_config']&~1
  seen=[]
  def cut(u,address,size,user):
   if address==target:seen.append((u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x40021000,0x40)),bytes(u.mem_read(0x20000124,4))));u.emu_stop()
  u.hook_add(UC_HOOK_CODE,cut)
  u.emu_start((0x08005528 if original else sym['case_transfer_control_5528'])|1,0x20001000,count=10000)
  assert len(seen)==1,(original,field16,field20,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append(seen[0])
 assert pair[0]==pair[1],(field16,field20,[(x[0],x[1][:16].hex(),x[2].hex()) for x in pair])
print('PASS_CASE_TRANSFER_RECONFIG_BOUNDARY',3)
