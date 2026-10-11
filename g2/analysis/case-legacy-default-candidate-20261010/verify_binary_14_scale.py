#!/usr/bin/env python3
"""Stock/source 0x0800018c signed quotient and remainder ABI."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_14_scale.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
values=[0,1,2,10,0x7fffffff,0x80000000,0xffffffff,0xfffffff6,0x12345678]
divisors=[0,1,2,10,0x7fffffff,0x80000000,0xffffffff,0xfffffff6]
rows=[]
for dividend,divisor in itertools.product(values,divisors):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.reg_write(UC_ARM_REG_R0,dividend);u.reg_write(UC_ARM_REG_R1,divisor);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x0800018c if original else sym['case_binary_14_scale'])|1,0x20001000,count=20000)
  row=[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(dividend,divisor,pair)
 rows.append([dividend,divisor,pair[0]])
out=dict(status='PASS_BINARY_14_SCALE_FULL_ABI',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_14_scale_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Signed 32-bit domain sampled, including divide-by-zero and INT_MIN; not an exhaustive 2^64 corpus.','Source C divide loop uses an explicit ARM ABI wrapper to return quotient R0 and remainder R1.','No public binary handler admission.'],rows=rows)
(D/'binary-14-scale-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
