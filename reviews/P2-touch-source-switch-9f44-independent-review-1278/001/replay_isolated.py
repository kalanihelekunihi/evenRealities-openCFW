from pathlib import Path
import json,hashlib,itertools,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-source-switch-9f44-independent-review-1278/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];invalid=word(0x9f90);base=word(0x9f94);disabled=word(0x9f98);rows=[]
for requested,current,enabled,frequency,high in itertools.product([0,1,2,3,0xffffffff],range(4),[0,1],[0,1,48000000],[0,0xa5a5a5a4,0xfffffffc]):
 old=(high&0xfffffffc)|current;u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(base,0x1000);u.mem_write(base+0x28,old.to_bytes(4,'little'));u.mem_write(base+0x30,(enabled<<31).to_bytes(4,'little'));u.mem_write(0x20000f20,frequency.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_R4,0x12345678);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,requested);reads=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,a,s,v,x:reads.append([a,s]) if a>=base or a==0x20000f20 else None);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a>=base else None);u.emu_start(0x9f45,0,count=100)
 expected_reads=[];expected_writes=[]
 if requested>1:ret=invalid
 else:
  expected_reads.append([base+0x28,4])
  if requested==current:ret=0
  else:
   if requested==0:expected_reads.append([base+0x30,4]);valid=bool(enabled)
   else:expected_reads.append([0x20000f20,4]);valid=frequency!=0
   if valid:ret=0;expected_reads.append([base+0x28,4]);expected_writes.append([base+0x28,4,(old&0xfffffffc)|requested])
   else:ret=disabled
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_R4)==0x12345678
 assert reads==expected_reads and writes==expected_writes,(requested,current,reads,expected_reads,writes)
 rows.append(dict(requested=requested,current=current,enabled=enabled,frequency=frequency,old=old,return_value=ret,reads=reads,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch source switch 9F44

Body 9F44..9F8E is 74 instruction bytes, excluding the adjacent NOP and three literal words. Unsigned requested selector greater than one returns the invalid-input literal without peripheral access. Otherwise actual 9F34 freshly reads current bits 1..0 at 40030028. An already-selected source returns zero without checking readiness or writing.

For a changed selector zero, freshly read 40030030 and require bit 31. For changed selector one, actual 9C38 reads RAM 20000F20 and requires a nonzero word. A failed prerequisite returns the disabled-source literal. A successful change freshly reads 40030028 again, replaces bits 1..0 with requested selector, stores once and returns zero. The frame restores R4 and SP. No polling loop occurs.

Original-instruction fixtures cover invalid requests, all four current selectors, both enable states, three RAM frequencies and three upper-register patterns. Counts are recorded in the receipt. Exact reads, writes, return and frame restoration agree with the separate model. Synthetic register values establish instruction behavior; physical clock readiness and concurrent changes remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=dict(base=base,invalid=invalid,disabled=disabled),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),hex(invalid),hex(disabled))
