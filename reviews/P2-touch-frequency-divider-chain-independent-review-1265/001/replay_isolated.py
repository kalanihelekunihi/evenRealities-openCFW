from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-frequency-divider-chain-1264-independent-review-1265/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[]
for inner,outer,selector,freq in itertools.product(range(4),range(4),[0,1,2],[0,1,48000000,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40030000,0x1000);u.mem_write(0x40030028,((inner<<2)|(outer<<6)).to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];reads=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x9f34,0x9c44,0x9c38]:calls.append(p);u.reg_write(UC_ARM_REG_R0,selector if p==0x9f34 else freq);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,lambda u,t,p,s,v,x:reads.append([p,s]) if p>=0x40000000 else None);u.emu_start(0x46f9,0,count=300)
 selected=freq if selector in[0,1] else 0
 rounded_inner=((selected+((1<<inner)>>1))&0xffffffff)>>inner
 expected=((rounded_inner+((1<<outer)>>1))&0xffffffff)>>outer
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 assert calls==([0x9f34,0x9c44] if selector==0 else([0x9f34,0x9c38] if selector==1 else[0x9f34])) and reads==[[0x40030028,4],[0x40030028,4]]
 rows.append(dict(inner_shift=inner,outer_shift=outer,selector=selector,frequency=freq,calls=calls,mmio_reads=reads,raw_return=expected))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch frequency divider chain

Actual46F8 freshly reads40030028, captures bits7..6 as outer shift, calls actual9F9C, adds half of1<<outer modulo2^32 and right shifts. Actual9F9C freshly reads the same address again, capturing bits3..2 as inner shift. It calls9F34; result0 selects9C44, result1 selects9C38, other results selectzero without a source call. It adds half of1<<inner modulo2^32 and right shifts. Both16-byteframes restore. Captured shifts can derive from different fresh register values; the test uses one unchanged synthetic word.

192 original-instruction fixtures cover all sixteen shiftpairs, three selectorresults and four frequencyvalues including overflow. Only selector andsource routines arecontrolled. Independent modular rounding calculations, exact two reads, helperselection, rawreturnandSP are checked. Physicalfrequency, actualselector/sourcebehavior and simultaneousregisterchanges remain unresolved. Bodies46F8..4714 and9F9C..9FCE exclude pools/NOP. No canonical admission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_spans=[[0x46f8,0x4714],[0x9f9c,0x9fce]],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'divider-chain fixtures')
