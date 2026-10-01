from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-register-fields-a01c-independent-review-1222/001/regenerated');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[]
for a,c,v,field,old in itertools.product([1,2,3],[0,1],[0,51,65535,65536,16777215,16777216],[0,3,31,32],[0,0xa5a5a5a5]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40010000,0x1000);u.mem_map(0x09000000,0x1000)
 for p in [0x40010400,0x40010500]:u.mem_write(p,old.to_bytes(4,'little'))
 for r,x in [(UC_ARM_REG_R0,a),(UC_ARM_REG_R1,c),(UC_ARM_REG_R2,v),(UC_ARM_REG_R3,field),(UC_ARM_REG_R4,4),(UC_ARM_REG_R5,5),(UC_ARM_REG_R6,6),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x09000001)]:u.reg_write(r,x)
 writes=[];reads=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,x,z:writes.append([p,s,x]) if p>=0x40000000 else None);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,p,s,x,z:reads.append([p,s]) if p>=0x40000000 else None);u.emu_start(0xa01d,0,count=200)
 valid=a in[2,3] and c==0 and v<(65536 if a==2 else 16777216) and field<=31
 target=0x40010400 if a==2 else 0x40010500;first=(old&(0xff0000ff if a==2 else 255))|((v<<8)&0xffffffff);second=(first&~248)|((field<<3)&255)
 assert writes==([[target,4,first],[target,4,second]] if valid else[]) and reads==([[target,4],[target,4]] if valid else[])
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==(0 if valid else 0x004a0001) and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and [u.reg_read(r) for r in [UC_ARM_REG_R4,UC_ARM_REG_R5,UC_ARM_REG_R6]]==[4,5,6]
 rows.append(dict(input0=a,input1=c,value=v,field=field,initial_word=old,valid=valid,writes=writes,reads=reads))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch two-stage register field update A01C

The supplied mode must be exactly 2 or 3, R1 must be zero, and R3 must be unsigned <=31. Mode 2 requires unsigned R2<65536 and selects 40010400; mode 3 requires unsigned R2<16777216 and selects 40010500. Rejected inputs return 004A0001 with no MMIO accesses. Mode 2 first reads the selected word, preserves bits31..24 and7..0, inserts R2 into bits23..8, and stores. Mode3 preserves bits7..0 and inserts R2 into bits31..8. Both then freshly read the selected address, replace bits7..3 with R3 shifted three, and store again. Valid calls return zero and restore R4/R5/R6 and the 16-byte frame.

288 original-instruction fixtures check predicates, exact two reads and ordered writes, raw return and restored registers. The second read observes the first stored word in these static synthetic fixtures. No inference assumes a physical register remains unchanged between accesses; fresh-read behavior is retained in pseudocode. The trailing NOP at A0AA and literal pool from A0AC are excluded; instruction body is A01C..A0AA. Physical bus behavior, concurrency and caller reachability remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0xa01c,0xa0aa],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'two-stage fixtures')
