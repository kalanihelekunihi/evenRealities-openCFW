#!/usr/bin/env python3
"""Stock/source timeout comparison with a deterministic advancing tick."""
from pathlib import Path
import subprocess
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
FW=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()[32:]
elf=HERE/'transfer_control_candidate.oracle.elf'
subprocess.run(['/tmp/iar-c-runtime-venv/bin/python',str(HERE/'verify_case_transfer_control.py')],check=True,capture_output=True)
with elf.open('rb') as stream:
 e=ELFFile(stream);sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()};segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
cases=[('ctl_ready',1,0x10000,0,0),('ctl_disable',2,0,0x400,0x20),('port_ready',8,0x1000000,0,0)]
for name,flags,mode,control,range_bits in cases:
 cfg=bytearray(0x40);cfg[0]=flags;cfg[4:8]=mode.to_bytes(4,'little')
 if name=='port_ready':cfg[24:28]=(1).to_bytes(4,'little')
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(FW)+4095)&~4095);u.mem_write(0x08000000,FW);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_map(0x20000000,0x10000);u.mem_write(0x20007000,bytes(cfg));u.mem_map(0x40021000,0x1000);u.mem_map(0x40007000,0x1000)
  u.mem_write(0x40021000,control.to_bytes(4,'little'));u.mem_write(0x40021008,range_bits.to_bytes(4,'little'))
  u.reg_write(UC_ARM_REG_R0,0x20007000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  target=0x08004eac if original else sym['case_tick_word2']&~1
  def tick(u,address,size,user):
   if address==target:
    old=int.from_bytes(u.mem_read(0x20000120,4),'little');u.mem_write(0x20000120,((old+1)&0xffffffff).to_bytes(4,'little'))
  u.hook_add(UC_HOOK_CODE,tick)
  u.emu_start((0x08005528 if original else sym['case_transfer_control_5528'])|1,0x20001000,count=100000)
  pair.append((u.reg_read(UC_ARM_REG_PC),u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x40021000,0x80)),bytes(u.mem_read(0x20000120,4))))
 assert pair[0][:3]==pair[1][:3],(name,[(hex(x[0]),x[1],x[2][:16].hex(),x[3].hex()) for x in pair])
 print('PASS',name,[x[3].hex() for x in pair])
print('PASS_CASE_TRANSFER_TIMEOUTS',len(cases))
