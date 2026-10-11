#!/usr/bin/env python3
"""Stock/source 0x080001b4 copy ABI shared by two binary route aliases."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_dispatch_copy.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
assert sym['case_binary_3d_dispatch']==sym['case_binary_forward_dispatch']
rows=[]
for length,dst_offset,src_offset,pattern in itertools.product([0,1,2,3,4,5,7,8,15,32,64],[0,1,2,3],[0,1,2,3],[0,1]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  dst=0x200001b4+dst_offset;src=0x20004000+src_offset
  data=bytes(((j*37+pattern*91)&255) for j in range(96))
  u.mem_write(src,data);u.mem_write(dst,b'\xa5'*80)
  u.reg_write(UC_ARM_REG_R0,dst);u.reg_write(UC_ARM_REG_R1,src);u.reg_write(UC_ARM_REG_R2,length);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  u.emu_start((0x080001b4 if original else sym['case_binary_3d_dispatch'])|1,0x20001000,count=10000)
  row=[u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200001b4,88)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(length,dst_offset,src_offset,pattern,pair)
 rows.append([length,dst_offset,src_offset,pattern,pair[0]])
out=dict(status='PASS_BINARY_DISPATCH_COPY_ABI',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_dispatch_copy_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Nonoverlapping source/destination; callers use separate frame and state buffers.','Alias names verified at same selected object address and stock target; full binary provider still withheld.'],rows=rows)
(D/'binary-dispatch-copy-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
