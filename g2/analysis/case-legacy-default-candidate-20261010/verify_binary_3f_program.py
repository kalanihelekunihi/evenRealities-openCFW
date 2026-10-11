#!/usr/bin/env python3
"""Compare complete stock 0x08009108 retry wrapper to source at bus/logger cuts."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
raw=blob[32:];elf=D/'binary_3f_program.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def z(u,p):
 b=bytearray()
 while len(b)<160:
  c=u.mem_read(p+len(b),1)[0]
  if not c:break
  b.append(c)
 return b.decode()
rows=[]
for index,count,failures,flag,counter in itertools.product([3,6],[1,2],[0,1,8,9],[0,1],[12,0xfffffffe]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw)
  u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20000080,counter.to_bytes(4,'little'))
  for j,v in enumerate([0x1234,0x5678,0x9abc]):u.mem_write(0x20000084+4*j,v.to_bytes(4,'little'))
  u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x20004000,b'\xae\x81')
  u.reg_write(UC_ARM_REG_R0,index);u.reg_write(UC_ARM_REG_R1,count);u.reg_write(UC_ARM_REG_R2,0x20004000)
  u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  calls=[];logs=[]
  def hook(uc,a,size,_):
   if a in [0x08000610,0x0010f000]:
    calls.append([uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_R3),count)).hex()])
    ret=0 if len(calls)<=failures else 0x4321
    uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08009170,0x0010f100]:
    fmt=z(uc,uc.reg_read(UC_ARM_REG_R0))
    args=[uc.reg_read(UC_ARM_REG_R1),uc.reg_read(UC_ARM_REG_R2),uc.reg_read(UC_ARM_REG_R3),int.from_bytes(uc.mem_read(uc.reg_read(UC_ARM_REG_SP),4),'little')] if '%d' in fmt else []
    logs.append([fmt,args]);uc.reg_write(UC_ARM_REG_R0,0xabc);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook)
  u.emu_start((0x08009108 if original else sym['case_binary_3f_program'])|1,0x20001000,count=5000)
  row=[calls,logs,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x2000007c,20)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(index,count,failures,flag,counter,pair)
 rows.append([index,count,failures,flag,counter,pair[0]])
out=dict(status='PASS_BINARY_3F_PROGRAM_WRAPPER',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_3f_program_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Bus 0x08000610 and logger 0x08009170 controlled; physical bus/interrupt effects not proven.','Caller indexes 3/6 and counts 1/2 plus synthetic data; not arbitrary MMIO claim.','Isolated child graph, no public binary provider admission.'],rows=rows)
(D/'binary-3f-program-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
