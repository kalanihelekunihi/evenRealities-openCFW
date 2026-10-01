from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-delay-interrupt-helpers-independent-review-1282/001/replay-output-independent');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for entry,value,mask in itertools.chain(itertools.product([0x4480],list(range(101))+[0xfffffffe,0xffffffff],[0,1]),itertools.product([0x4492,0x449a],[0,1,2,3,0xffffffff],[0,1])):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_R0,value);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_LR,0x09000001);pcs=[]
 def code(u,p,s,x):
  pcs.append(p)
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(entry|1,0,count=300)
 q=((value+2)&0xffffffff)>>2
 expected=0 if entry==0x4480 else (mask if entry==0x4492 else value);expected_mask=mask if entry==0x4480 else (1 if entry==0x4492 else value&1)
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_PRIMASK)==expected_mask
 if entry==0x4480:assert pcs.count(0x4486)==q and pcs.count(0x4488)==q
 rows.append(dict(entry=entry,input=value,initial_primask=mask,return_value=expected,final_primask=expected_mask,loop_iterations=q if entry==0x4480 else None,pcs=pcs))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch delay and interrupt-mask helpers

4480..4492 is an 18-byte arithmetic busy loop. Compute q = u32(input + 2) >> 2. If q is nonzero, increment once and subtract two each iteration, so the net decrement is one and exactly q iterations occur. Return R0 zero. Two NOP instructions are executed according to the branch path. PRIMASK is preserved. This establishes instruction counts, not physical elapsed time.

4492..449A is an eight-byte helper: return prior PRIMASK in R0, disable configurable interrupts, return through LR. 449A..44A0 is a six-byte helper: set PRIMASK from R0, whose implemented bit is bit zero, preserve R0, return through LR. Neither uses a stack frame.

Original-instruction fixtures cover delay inputs zero through 100 and the two addition-wrap inputs, with both initial masks. Mask helpers cover five raw inputs and both initial masks. Counts are derived in the receipt; exact loop iteration counts, returns and masks are checked. No C implementation or canonical admission. External interrupt dispatch and physical timing remain unresolved.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
