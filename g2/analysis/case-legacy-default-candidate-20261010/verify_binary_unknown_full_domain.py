#!/usr/bin/env python3
"""Authenticated full-entry stock/source oracle for binary unknown fallback."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();sha=hashlib.sha256(blob).hexdigest();assert sha=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:]
elf=D/'binary_unknown.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def z(u,p):
 b=bytearray()
 while len(b)<64:
  v=u.mem_read(p+len(b),1)[0]
  if not v:break
  b.append(v)
 return b.decode()
rows=[]
for op,dst,n,flag,logret in itertools.product([x for x in range(256) if x not in {0x06,0x14,0x3e,0x3f,0x41,0x50,0x51,0x56,0x5c,0x5d,0x5e,0x5f,0x68}],[2],[0,1,4,20],[0,1,0x7f],[0,0x13579bdf]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0);u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes([op,0,dst])+bytes(253));u.mem_write(0x200000bf,bytes([flag]));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_R1,n);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  events=[]
  def hook(uc,a,size,_):
   if a in [0x08009170,0x0010f200]:
    fmt=z(uc,uc.reg_read(UC_ARM_REG_R0));events.append([fmt,uc.reg_read(UC_ARM_REG_R1) if '%02x' in fmt else None]);uc.reg_write(UC_ARM_REG_R0,logret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08000e1c if original else sym['case_binary_unknown_candidate'])|1,0x20001000,count=10000)
  assert u.reg_read(UC_ARM_REG_PC)==0x20001000,(op,dst,original,hex(u.reg_read(UC_ARM_REG_PC)))
  pair.append([events,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200000bf,1)).hex()])
 assert pair[0]==pair[1],(op,dst,n,flag,logret,pair)
 rows.append([op,dst,n,flag,logret,pair[0]])
out=dict(status='PASS_BINARY_UNKNOWN_FULL_OPCODE_DOMAIN',cases=len(rows),image_sha256=sha,source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_unknown_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['All 243 non-special opcode bytes with destination byte 2; allocated 256 bytes even at logical length zero.','Logger is controlled boundary; no UART or physical effects.','This isolated fallback is not full case_binary_command.'],rows=rows)
(D/'binary-unknown-full-domain-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
