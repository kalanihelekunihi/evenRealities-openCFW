#!/usr/bin/env python3
"""Compare stock 0x080099e8 shadowed setter with source at program cut."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=blob[32:];elf=D/'binary_3f_set.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for index,value,equal,result in itertools.product([3,4,5,6],[0,0xae,0x81,0x103],[False,True],[0,1,0x76543210]):
 pair=[]
 for original in (True,False):
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  cached=(value&255) if equal else ((value+7)&255)
  u.mem_write(0x20000090+index,bytes([cached]));u.reg_write(UC_ARM_REG_R0,index);u.reg_write(UC_ARM_REG_R1,value)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[]
  def hook(uc,a,size,_):
   if a in [0x08009108,0x0010f000]:
    p=uc.reg_read(UC_ARM_REG_R2)
    calls.append([uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),bytes(uc.mem_read(p,1)).hex()])
    uc.reg_write(UC_ARM_REG_R0,result);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x080099e8 if original else sym['case_binary_3f_set'])|1,0x20001000,count=1000)
  row=[calls,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20000090,16)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(index,value,equal,result,pair)
 rows.append([index,value,equal,result,pair[0]])
out=dict(status='PASS_BINARY_3F_SHADOW_SET',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_3f_set_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Caller domain indexes 3 through 6; no arbitrary index safety claim.','Program lower 0x08009108 controlled; physical output effect unverified.','Isolated setter, no public binary handler admission.'],rows=rows)
(D/'binary-3f-set-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
