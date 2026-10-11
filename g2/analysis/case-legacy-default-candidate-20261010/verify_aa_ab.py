#!/usr/bin/env python3
"""Stock/source aa/ab table branch ABI comparisons."""
from pathlib import Path
import hashlib,json,itertools
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2];image=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(image).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=image[32:];elf=D/'aa_ab.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[];hooks={0x0800d1bc:('aa_first',0),0x0010f900:('aa_first',0),0x0800d218:('aa_second',1),0x0010fa00:('aa_second',1),0x08003558:('ab_child',2),0x0010fb00:('ab_child',2)}
for opcode,length,flag,returns in itertools.product([0xaa,0xab],[0,1,8],[0,1,0x7f],[(0,0,0),(0x12345678,0x87654321,0xfeedbeef)]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for address,data in segments:u.mem_write(address,data)
  u.mem_write(0x20004000,bytes([opcode,0x55])+bytes(30));u.mem_write(0x200000bf,bytes([flag]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[];writes=[]
  def code(uc,address,size,user):
   if address in hooks:
    name,index=hooks[address];events.append([name,uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,returns[index]);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR));return
   if address==0x08009170:raise AssertionError('unexpected logger')
  def write(uc,access,address,size,value,user):
   if not 0x20007fc0<=address<0x20008000:writes.append([address,size,value])
  u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,write)
  u.emu_start((0x08000928 if original else sym['case_legacy_aa_branch' if opcode==0xaa else 'case_legacy_ab_branch'])|1,0x20001000,count=10000)
  pair.append(dict(return_value=u.reg_read(UC_ARM_REG_R0),events=events,writes=writes,flag=bytes(u.mem_read(0x200000bf,1)).hex()))
 assert pair[0]==pair[1],(opcode,length,flag,returns,pair)
 rows.append(dict(opcode=opcode,length=length,flag=flag,returns=returns,comparison=pair[0]))
out=dict(status='PASS_AA_AB_BOUNDED_BRANCHES',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/control_aa_ab.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Only aa and ab table branches; three lower children controlled.','No public legacy handler or physical lower effects.'],rows=rows)
(D/'aa-ab-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
