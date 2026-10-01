from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-frequency-register-chain-independent-review-1267/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[]
for inner,outer,selector,trim,enabled in itertools.product(range(4),range(4),range(4),range(8),[0,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40030000,0x1000);u.mem_map(0x09000000,0x1000)
 for a,v in [(0x40030028,(inner<<2)|(outer<<6)|selector),(0x40030030,enabled<<31),(0x40030f08,trim),(0x20000f20,48000000)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);reads=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,p,s,v,x:reads.append([p,s]) if p>=0x20000000 and p<0x2000e000 or p>=0x40000000 else None);u.emu_start(0x46f9,0,count=300)
 source=(24000000+4000000*trim if enabled else 0) if selector==0 else(48000000 if selector==1 else 0)
 intermediate=((source+((1<<inner)>>1))&0xffffffff)>>inner;expected=((intermediate+((1<<outer)>>1))&0xffffffff)>>outer
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 required=[[0x40030028,4]]*3
 if selector==0:required+=[[0x40030030,4]]+([[0x40030f08,4]] if enabled else[])
 elif selector==1:required+=[[0x20000f20,4]]
 assert reads==required
 rows.append(dict(inner_shift=inner,outer_shift=outer,selector=selector,trim=trim,enabled=enabled,source=source,raw_return=expected,reads=reads))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch frequency register chain with actual source helpers

Actual9F34 freshly reads40030028 and returns bits1..0. Actual9C38 reads the frequencyword at RAM20000F20. Actual9C44 freshly reads40030030 and returnszero if bit31 is clear. If set, it reads40030F08 and uses only bits2..0, computing24000000+4000000*index. Its exact arithmetic sequence agrees with this polynomial over the eight possibleindices. Rawregisterfrequency is a code-derived value, not independently measuredhardwarefrequency.

1024 original-instruction fixtures execute46F8,9F9C,9F34 and the selected source helper without any helper replacement. They cover all shiftpairs, all four selectors, eight trimindices and both bit31states. Exactfreshreadorder, independently calculated sourcedivision/rounding andSP are checked. Syntheticregistervalues andRAMword are supplied; physicalclockmeaning and concurrentchanges remain unresolved. Actual9C44 body9C44..9C72,9C38..9C3E and9F34..9F3E exclude adjacentNOP/pools. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'actual source/divider chains')
