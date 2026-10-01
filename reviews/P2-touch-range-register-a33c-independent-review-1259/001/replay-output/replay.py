from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-range-register-a33c-1258-independent-review-1259/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[]
for value,old in itertools.product([0,16,17,32,33,48,0xffffffff],[0,0xa5a5a5a5,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x40100000,0x1000);u.mem_write(0x40100030,old.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);reads=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,v,x:writes.append([p,s,v]));u.hook_add(UC_HOOK_MEM_READ,lambda u,t,p,s,v,x:reads.append([p,s]) if p>=0x40000000 else None);u.emu_start(0xa33d,0,count=100)
 mode=0 if value<=16 else(1 if value<=32 else 2);first=(old&~3)|mode;second=(first&~16)|(16 if mode else 0)
 assert reads==[[0x40100030,4],[0x40100030,4]] and writes==[[0x40100030,4,first],[0x40100030,4,second]]
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==3 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(input=value,initial_word=old,mode=mode,reads=reads,writes=writes,raw_return=3))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch range-selected register A33C

Unsigned input<=16 selects mode0, input17..32 selects mode1, and input>32 selects mode2. A fresh word read at40100030 replaces bits1..0 with thatmode and stores. A second fresh read clears bit4 and sets it iffmode is nonzero, thenstores. RawR0 returns3, not a successstatus. No frame, helper or inputrejection exists. BodyA33C..A36E excludes trailingNOP/literalpool.

Twenty-one original-instruction fixtures check unsignedthresholds, three initialwords, two reads, orderedwrites, rawreturnandSP. The second read sees the first store in these static synthetic fixtures; physicalfreshread changes and registermeaning remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0xa33c,0xa36e],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'range-register fixtures')
