#!/usr/bin/env python3
"""Stock/source isolated 0x0800373c three-read failure path."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_5e_retry_failure.elf'
with elf.open('rb') as f:
 e=ELFFile(f);segments=[(s['p_vaddr'],s.data()) for s in e.iter_segments() if s['p_type']=='PT_LOAD'];sym={s.name:s['st_value'] for s in e.get_section_by_name('.symtab').iter_symbols()}
def z(u,p):
 b=bytearray()
 while len(b)<80:
  v=u.mem_read(p+len(b),1)[0]
  if not v:break
  b.append(v)
 return b.decode()
rows=[]
for mode,flag,errors in itertools.product([0,1,2],[0,1,0x7f],[(1,2,3),(0x1234,0x5678,0x9abc)]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x20004000,bytes(range(16)));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x200001a4,b'\xa5'*16)
  u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[];reads=[0]
  def hook(uc,a,size,_):
   if a in [0x08002f46,0x0010f000]:
    ev.append(['mode']);uc.reg_write(UC_ARM_REG_R0,mode);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08004bf4,0x0010f100]:
    ev.append(['init']);uc.reg_write(UC_ARM_REG_R0,0x4321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x0800497c,0x0010f200]:
    assert uc.reg_read(UC_ARM_REG_R0)==0x200001a4
    p=uc.reg_read(UC_ARM_REG_R1);ev.append(['read',bytes(uc.mem_read(0x200001a4,16)).hex()]);uc.mem_write(p,errors[reads[0]].to_bytes(4,'little'));reads[0]+=1;uc.reg_write(UC_ARM_REG_R0,1);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08004958,0x0010f300]:
    ev.append(['wait',uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,0x4321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08009170,0x0010f500]:
    fmt=z(uc,uc.reg_read(UC_ARM_REG_R0));ev.append(['log',fmt,uc.reg_read(UC_ARM_REG_R1) if '%x' in fmt else None]);uc.reg_write(UC_ARM_REG_R0,0x4321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08004b20,0x0010f400]:
    ev.append(['finish']);uc.reg_write(UC_ARM_REG_R0,0x4321);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x0800373c if original else sym['case_binary_5e_retry_failure_candidate'])|1,0x20001000,count=3000)
  row=[ev,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200001a4,16)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(mode,flag,errors,pair)
 rows.append([mode,flag,errors,pair[0]])
out=dict(status='PASS_BINARY_5E_THREE_READ_FAILURE',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_5e_retry_failure_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Precondition: all three flash reads return nonzero; success/write/verify branches excluded.','Flash init/read/wait/finalize and formatter controlled; physical flash effects unproven.','Branch-only candidate; not full case_binary_5e_apply and not in linked/public provider graph.'],rows=rows)
(D/'binary-5e-retry-failure-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
