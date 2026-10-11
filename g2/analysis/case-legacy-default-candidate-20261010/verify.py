#!/usr/bin/env python3
"""Bounded fixed-image comparison for legacy no-action return branches."""
from pathlib import Path
import hashlib,json,struct,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=image[32:];elf=D/'default.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD']
 sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
assert sym['case_legacy_default_branch']&~1==0x100000
rows=[];opcodes=[0x00,0x01,0x7f,0xa6,0xa7,0xa8,0xa9,0xac,0xad,0xb1,0xd5,0xe0,0xfe]
for opcode,length,flag in itertools.product(opcodes,[1,2,8],[0,1,0x7f]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_write(0x20004000,bytes([opcode,0x55])+bytes(30));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087c,b'\xa5')
  u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  lower=[];writes=[]
  def code(uc,address,size,user):
   if address in (0x08009170,0x08006b98,0x08006b80):lower.append(hex(address));uc.emu_stop()
  def write(uc,access,address,size,value,user):
   if address<0x20007fc0 or address>=0x20008000:writes.append([address,size,value])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x08000928 if original else sym['case_legacy_default_branch'])|1,0x20001000,count=10000)
  assert not lower,(opcode,lower)
  pair.append((u.reg_read(UC_ARM_REG_PC),u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200000bf,1)),bytes(u.mem_read(0x2000087c,1)),writes))
 assert pair[0]==pair[1],(opcode,length,flag,pair)
 rows.append(dict(opcode=opcode,length=length,initial_flag=flag,return_value=pair[0][1]))
out=dict(status='PASS_BOUNDED_DEFAULT_BRANCH',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/default.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),opcodes=[hex(x) for x in opcodes],limits=['Only no-action return branches; no public case_legacy_command provider.','Callee-saved registers and stack are not compared; fixed-image execution uses Cortex-M0 Unicorn, not physical CASE.'],rows=rows)
(D/'comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
