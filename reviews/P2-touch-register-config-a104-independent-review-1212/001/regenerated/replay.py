from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-register-config-a104-independent-review-1212/001/regenerated');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[];pcs=set()
for a,c in itertools.product([0,1,2,3,4,257,258,259,0xffffffff],[0,1,2,63,64,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x40010000,0x1000);u.mem_write(0x40010000,b'\xa5'*4);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_R0,a);u.reg_write(UC_ARM_REG_R1,c);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);writes=[];reads=[]
 def code(u,p,s,x):
  pcs.add(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,p,s,v,x:reads.append([p,s]) if p==0x40010000 else None);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,v,x:writes.append([p,s,v]));u.emu_start(0xa105,0,count=100)
 valid=(a==1 and c<=1) or (((a-2)&255)<=1 and c==0)
 expected=0 if valid else 0x004a0001;assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 assert writes==([[0x40010000,4,0x8000ff00|((a<<6)&255)|(c&63)]] if valid else[])
 assert reads==([[0x40010000,4]] if valid else [])
 if not valid:assert bytes(u.mem_read(0x40010000,4))==b'\xa5'*4
 rows.append(dict(input0=a,input1=c,valid=valid,return_value=expected,writes=writes,readback=reads))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch configuration register command A104

Exact A104..A13C instructions accept `(R0==1 && unsignedR1<=1) || (((R0-2) modulo256)<=1 && R1==0)`. The second test truncates to eight bits, so supplied inputs258/259 withR1zero are accepted as well as2/3. Accepted inputs write one word to40010000: `8000FF00 | ((R0<<6)&255) | (R1&63)` then perform one fresh word read from that same address and return zero. The read value does not affect the return. Rejected inputs return literal004A0001 without a register write. No stack frame or helper calls occur; volatile command semantics beyond the word write remain unresolved.

Fifty-four original-instruction fixtures exercise canonical values, large aliases, mode boundaries andFFFF_FFFF. Independent predicate/postconditions check exactwriteaddress,width,value,unchangedMMIOonrejection,rawreturnandSP. SyntheticMMIOdoesnotprovephysicalcommandinterpretation. No canonicaladmission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0xa104,0xa13c],body_sha256=h(d[0x6e04:0x6e3c]),observed_pcs=sorted(pcs),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'configuration fixtures')
