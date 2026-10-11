#!/usr/bin/env python3
"""Stock/source 0x08009f18 sensor conversion at read/scale cuts."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_14_read_b.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
rows=[]
for mode,sample,fail,scaled in itertools.product([0,1,63,64,128,255],[0,1,0x7fff,0x8000,0xffff,0x1234],['none','byte','word'],[0,0x12345678]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,(0xdeadbeef).to_bytes(4,'little'));u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[]
  def hook(uc,a,size,_):
   if a in [0x0800a124,0x0010f000]:
    p=uc.reg_read(UC_ARM_REG_R1);ev.append(['byte',uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(p,1)).hex()]);uc.mem_write(p,bytes([mode]));uc.reg_write(UC_ARM_REG_R0,1 if fail=='byte' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x0800a074,0x0010f100]:
    p=uc.reg_read(UC_ARM_REG_R1);ev.append(['word',uc.reg_read(UC_ARM_REG_R0),bytes(uc.mem_read(p,4)).hex()]);uc.mem_write(p,sample.to_bytes(4,'little'));uc.reg_write(UC_ARM_REG_R0,1 if fail=='word' else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x0800018c,0x0010f200]:
    ev.append(['scale',uc.reg_read(UC_ARM_REG_R0),uc.reg_read(UC_ARM_REG_R1)]);uc.reg_write(UC_ARM_REG_R0,scaled);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x08009f18 if original else sym['case_binary_14_read_b'])|1,0x20001000,count=2000)
  row=[ev,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x20004000,4)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(mode,sample,fail,scaled,pair)
 rows.append([mode,sample,fail,scaled,pair[0]])
out=dict(status='PASS_BINARY_14_READ_B',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_14_read_b_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Byte/word readers and scale controlled; physical sensor transaction remains separate.','Mode, sign and failure branches sampled; no public binary provider admission.'],rows=rows)
(D/'binary-14-read-b-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
