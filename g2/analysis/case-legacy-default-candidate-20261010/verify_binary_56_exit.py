#!/usr/bin/env python3
"""Stock/source 0x080012e4 exit wrapper with controlled task/GPIO/logger."""
from pathlib import Path
import hashlib,itertools,json
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile
D=Path(__file__).resolve().parent;root=D.parents[2]
blob=(root/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes();assert hashlib.sha256(blob).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374';raw=blob[32:];elf=D/'binary_56_exit.elf'
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
for task,flag,seed in itertools.product([0,0x12345678,0xffffffff],[0,1,0x7f],[0,1,0x4321]):
 pair=[]
 for original in [True,False]:
  u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
  u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw);u.mem_map(0x20000000,0x10000);u.mem_map(0x00100000,0x10000)
  for a,b in segments:u.mem_write(a,b)
  u.mem_write(0x200000d0,task.to_bytes(4,'little'));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x2000087e,b'\xa5');u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
  ev=[]
  def hook(uc,a,size,_):
   names={0x0800ab26:'cancel',0x0010f000:'cancel',0x08006b80:'a',0x0010f100:'a',0x08006b98:'b',0x0010f200:'b'}
   if a in names:
    ev.append([names[a],uc.reg_read(UC_ARM_REG_R0)]);uc.reg_write(UC_ARM_REG_R0,(seed+len(ev))&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
   elif a in [0x08009170,0x0010f300]:
    ev.append(['log',z(uc,uc.reg_read(UC_ARM_REG_R0))]);uc.reg_write(UC_ARM_REG_R0,(seed+len(ev))&0xffffffff);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
  u.hook_add(UC_HOOK_CODE,hook);u.emu_start((0x080012e4 if original else sym['case_binary_56_exit'])|1,0x20001000,count=1000)
  row=[ev,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x2000087e,1)).hex(),u.reg_read(UC_ARM_REG_PC)]
  assert row[-1]==0x20001000,row
  pair.append(row)
 assert pair[0]==pair[1],(task,flag,seed,pair)
 rows.append([task,flag,seed,pair[0]])
out=dict(status='PASS_BINARY_56_EXIT_WRAPPER',cases=len(rows),image_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256((root/'g2/components/case/legacy_default_candidate_20261010/binary_56_exit_candidate.c').read_bytes()).hexdigest(),elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),limits=['Cancel 0x0800ab26, GPIO 0x08006b80/0x08006b98 and logger 0x08009170 controlled; physical effects unverified.','Exit wrapper sourced, but lower effects and public binary handler remain open.'],rows=rows)
(D/'binary-56-exit-comparison.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(rows))
