#!/usr/bin/env python3
"""Bounded actual stock/C comparison of CASE 0x5e flash apply, including writes."""
from pathlib import Path
import hashlib, itertools, json
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import *
from elftools.elf.elffile import ELFFile

D=Path(__file__).resolve().parent
ROOT=D.parents[3]
BLOB=(ROOT/'g2/blobs/official/g2-2.2.6.10/firmware_box.bin').read_bytes()
assert hashlib.sha256(BLOB).hexdigest()=='36ca0c13558f252af286ae2b36b5e576d087d21d37b15d778e7da9f502a70374'
ELF=D/'case-binary-whole.elf'
with ELF.open('rb') as f:
 e=ELFFile(f)
 SEG=[(x['p_vaddr'],x.data()) for x in e.iter_segments() if x['p_type']=='PT_LOAD']
 SYM={x.name:x['st_value'] for x in e.get_section_by_name('.symtab').iter_symbols()}
NATIVE={0x08002f46:'mode',0x08004bf4:'init',0x0800497c:'read',0x08004958:'wait',0x08004b94:'program',0x08004b20:'finish',0x08009170:'log'}
SOURCE={SYM['case_binary_5e_'+n]&~1:kind for n,kind in [('flash_mode','mode'),('flash_init','init'),('flash_read','read'),('wait','wait'),('flash_program','program'),('flash_finish','finish'),('failure_log','log')]}
def cstr(u,p):
 b=bytearray()
 for i in range(80):
  x=u.mem_read(p+i,1)[0]
  if x==0:break
  b.append(x)
 return b.decode()
def run(stock,mode,flag,reads,program,pattern):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M0)
 raw=BLOB[32:];u.mem_map(0x08000000,(len(raw)+4095)&~4095);u.mem_write(0x08000000,raw)
 u.mem_map(0x00100000,0x10000);u.mem_map(0x20000000,0x10000)
 for a,b in SEG:u.mem_write(a,b)
 u.mem_write(0x20004000,bytes(pattern));u.mem_write(0x200000bf,bytes([flag]));u.mem_write(0x200001a4,b'\xa5'*16)
 u.reg_write(UC_ARM_REG_R0,0x20004000);u.reg_write(UC_ARM_REG_SP,0x20008000);u.reg_write(UC_ARM_REG_LR,0x20001001)
 events=[];read_count=0;write_count=0
 def hook(uc,a,size,_):
  nonlocal read_count,write_count
  kind=(NATIVE if stock else SOURCE).get(a)
  if not kind:return
  r0=uc.reg_read(UC_ARM_REG_R0);r1=uc.reg_read(UC_ARM_REG_R1);r2=uc.reg_read(UC_ARM_REG_R2);r3=uc.reg_read(UC_ARM_REG_R3)
  if kind=='mode':events.append(['mode']);ret=mode
  elif kind=='init':events.append(['init']);ret=0x4321
  elif kind=='read':
   assert r0==0x200001a4
   events.append(['read',bytes(uc.mem_read(r0,16)).hex()]);uc.mem_write(r1,(0x1234+read_count).to_bytes(4,'little'))
   ret=reads[min(read_count,len(reads)-1)];read_count+=1
  elif kind=='wait':events.append(['wait',r0]);ret=0x4321
  elif kind=='program':events.append(['program',r0,r1,r2,r3]);ret=program[min(write_count,len(program)-1)];write_count+=1
  elif kind=='finish':events.append(['finish']);ret=0x4321
  else:
   s=cstr(uc,r0);events.append(['log',s,r1 if '%x' in s else None]);ret=0x4321
  uc.reg_write(UC_ARM_REG_R0,ret);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 try:u.emu_start((0x0800373c if stock else SYM['case_binary_5e_apply'])|1,0x20001000,count=10000)
 except Exception as ex:raise RuntimeError((stock,mode,flag,reads,program,events,hex(u.reg_read(UC_ARM_REG_PC)),hex(u.reg_read(UC_ARM_REG_LR)))) from ex
 assert u.reg_read(UC_ARM_REG_PC)==0x20001000
 return [events,u.reg_read(UC_ARM_REG_R0),bytes(u.mem_read(0x200001a4,16)).hex()]
rows=[]
for mode,flag,reads,program,pattern in itertools.product(
 [0,1,2],[0,1],[(0,),(1,0),(1,1,0),(1,1,1)],[(0,0),(1,0),(0,1),(1,1)],
 [list(range(16)),[0]*16,[255-i for i in range(16)]]):
 a=run(True,mode,flag,reads,program,pattern);b=run(False,mode,flag,reads,program,pattern)
 assert a==b,(mode,flag,reads,program,pattern,a,b)
 rows.append([mode,flag,reads,program,pattern,a])
out={'status':'PASS_CASE_FLASH_APPLY_STOCK_SOURCE','cases':len(rows),'stock_sha256':hashlib.sha256(BLOB).hexdigest(),'elf_sha256':hashlib.sha256(ELF.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'g2/components/case/legacy_default_candidate_20261010/flash_apply_candidate.c').read_bytes()).hexdigest(),'limits':['Control lower hooks at flash mode/init/read/wait/program/finalize/log; physical flash effects not executed.','Only allocated 16-byte input, shown mode/flag/status/pattern domains; no arbitrary pointer or hardware fault proof.'],'rows':rows}
(D/'case-flash-apply-whole-comparison.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'],out['cases'])
