from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-clock-startup-independent-review-1255/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[]
for old,raw in itertools.product([0,0xffffffff,0xa5a5a5a5],[0,1,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40030000,0x1000);u.mem_map(0x09000000,0x1000)
 for a in [0x40030028,0x4003002c]:u.mem_write(a,old.to_bytes(4,'little'))
 u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0xa33c,0x9c80,0x9f44,0x4734,0xa188]:
   calls.append(dict(pc=p,args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]));u.reg_write(UC_ARM_REG_R0,0 if p==0x9f44 else raw);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,v,x:writes.append([p,s,v]) if p>=0x40000000 else None);u.emu_start(0x45d1,0,count=300)
 assert [x['pc'] for x in calls]==[0xa33c,0x9c80,0x9f44,0x4734,0xa188,0x9c80,0x9f44,0xa33c,0x4734]
 assert [calls[i]['args'][0] for i in [0,1,2,4,5,6,7]]==[48,0x016e3600,0,0,0x02dc6c00,0,48]
 first=old&~12;second=first&~192
 assert writes==[[0x40030030,4,0x80000000],[0x40030028,4,first],[0x40030028,4,second],[0x4003002c,4,old|0x80000000],[0x40030028,4,second],[0x40030028,4,second]]
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_R0)==raw
 rows.append(dict(initial_word=old,helper_return=raw,calls=calls,writes=writes,return_value=raw))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch clock startup bounded path45D0

Actual45D0 saves R4/R5/R6/LR, calls A33C(48), writes80000000 at40030030, calls9C80(016E3600), then9F44(0). It freshly clears bits3..2 at40030028 and then freshly clears bits7..6. Calls4734 andA188(0) follow. It freshly sets bit31 at4003002C, calls9C80(02DC6C00), then actual45AC. That wrapper calls9F44(0); on its tested zero return it freshly clears bits3..2 at40030028 and restores its frame. A nonzero return would call breakpoint helper45A6; that path is not dynamically tested here. Back in45D0 a fresh bit7..6 clear precedes A33C(48) and4734, then restored-frame return retaining raw4734result.

Nine original-instruction fixtures vary three initialregisterpatterns and three controlled rawreturns. Five deeperhelperentries remain controlled;9F44returnszero throughout. Exactcallorder/selectedarguments, six ordered MMIOwrites and rawreturn/SP are checked. Helpers do not mutate memory under this contract; fresh reads and possible real changes remain separate. Hardwareclockmeaning, wait/timingandbreakpointbehavior remain unresolved. Body45D0..4628 excludes its literals. No canonical admission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0x45d0,0x4628],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'clock-startup paths')
