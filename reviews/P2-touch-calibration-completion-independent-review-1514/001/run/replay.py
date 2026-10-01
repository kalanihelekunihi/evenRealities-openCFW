from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-calibration-completion-independent-review-1514/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();divisor=struct.unpack_from('<I',d,0x69bc-0x3300)[0];cleanup=struct.unpack_from('<I',d,0x69c0-0x3300)[0];rows=[]
for budget,ready_at,freq,seed in itertools.product([0,1,3],[0,1,3,None],[0,48000000,0xffffffff],[0,123]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=0x20002100;X=0x20002200;P=0x40000000
 for a,v in [(D,F),(F,freq),(F+8,X),(X,P)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.reg_write(UC_ARM_REG_R0,seed);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];polls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x5fa4:calls.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]);u.reg_write(UC_ARM_REG_R0,budget);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 def read(u,t,a,s,v,x):
  if a==P+256 and not writes:
   val=256 if ready_at is not None and len(polls)>=ready_at else 0;polls.append(val);u.mem_write(a,val.to_bytes(4,'little'))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_READ,read);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a==P+256 else None);u.emu_start(0x6981,0,count=3000)
 observed=ready_at is not None and ready_at<=budget;expected=budget-ready_at if observed else 0;count=ready_at+1 if observed else budget+1
 assert calls==[[seed,freq//divisor,5]] and len(polls)==count and writes==[[P+256,4,cleanup]] and u.reg_read(UC_ARM_REG_R0)==expected and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(budget=budget,ready_at=ready_at,freq=freq,seed=seed,polls=polls,result=expected,calls=calls,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Calibration completion at 6980\n\nThe 58-byte body [6980,69BA) is followed by alignment and two literals. Resolve peripheral through descriptor/configuration pointers. Original A6C0 divides configuration word0 by literal1000000. Call5FA4(originalR0,quotient,5), retaining its countdown. Repeatedly read peripheral word100: stop when bit8 is set, or countdown is zero; otherwise decrement and repeat. Always write cleanup literalC1011111 to that register and read it back. Return remaining countdown, preserving zero even if ready arrives on the final check. Restore16-byte frame.\n\nThe72 original-instruction fixtures check exact budget+1 maximum reads, immediate/delayed/absent readiness, real division, exact5FA4 arguments, cleanup and frame. 5FA4 is controlled and readiness reads are explicitly modeled. Physical timing/register semantics remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),divisor=divisor,cleanup=cleanup,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
