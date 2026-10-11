#!/usr/bin/env python3
"""Authenticated stock/source opcode 0x5f branch, controlled fill/send."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_5f.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for length,flag,fill in itertools.product([0,1,4,12,20],[0,1,0x7f],[bytes(16),bytes(range(16)),bytes([0xff])*16]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([0x5f,0,2])+bytes(253));u.mem_write(0x200000bf,bytes([flag]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[];stop=[False]
  def hook(uc,a,size,_):
   if a in [0x08002f88,0x0010f000]:
    p=uc.reg_read(UC_ARM_REG_R0);events.append(['fill',bytes(uc.mem_read(p-4,4)).hex()]);uc.mem_write(p,fill);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x0800680c,0x0010f100]:
    p=uc.reg_read(UC_ARM_REG_R0);n=uc.reg_read(UC_ARM_REG_R1);events.append(['send',n,bytes(uc.mem_read(p,n)).hex()]);stop[0]=True;uc.emu_stop()
   elif a==0x08009170:raise AssertionError('unexpected logger')
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000e1c if original else sym['case_binary_5f_candidate'])|1,0x20001000,count=10000)
  assert stop[0],(length,flag,original,events)
  pair.append([events,bytes(u.mem_read(0x200000bf,1)).hex()])
 assert pair[0]==pair[1],(length,flag,fill.hex(),pair)
 rows.append([length,flag,fill.hex(),pair[0]])
out=dict(status='PASS_BINARY_5F_BOUNDED',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_5f_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Destination byte 2; opcode 0x5f; allocated 256-byte input at every logical length.','Stops at send entry; fill child is controlled with three vectors. Physical send and producer semantics excluded.','Isolated branch, not public case_binary_command.'],rows=rows)
(D/'binary-5f-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
