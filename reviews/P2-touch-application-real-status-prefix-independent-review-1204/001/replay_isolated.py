from pathlib import Path
import json,hashlib,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-application-real-status-prefix-independent-review-1204/001/regenerated');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();lit={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in range(0x3ea4,0x3ec4,4)};rows=[]
for failure in [0]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x200004c0,d[0x828c:0x8650]);u.mem_map(0x40000000,0x100000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_PRIMASK,1);calls=[];writes=[];pcs=[]
 targets=[0x44c4,0x3638,0x3ee0,0x395c,0x3658,0x3ca4,0x3678,0x38e0,0x5dd8,0x5d90]
 def code(u,p,s,x):
  pcs.append(p)
  if p in [0x3cc6,0x3d50]:u.emu_stop();return
  if p in targets:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];calls.append(dict(pc=p,args=args));u.reg_write(UC_ARM_REG_R0,failure if p==0x44c4 else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0x3cb5,0,count=1000)
 assert u.reg_read(UC_ARM_REG_SP)==0x2000eff8
 if failure:assert u.reg_read(UC_ARM_REG_PC)==0x3cc6 and [x['pc'] for x in calls]==targets[:2] and u.reg_read(UC_ARM_REG_PRIMASK)==1
 else:
  assert u.reg_read(UC_ARM_REG_PC)==0x3d50 and [x['pc'] for x in calls]==targets and u.reg_read(UC_ARM_REG_PRIMASK)==0
  assert calls[2]['args'][:3]==[lit[0x3eac],lit[0x3ea8],lit[0x3ea4]]
  assert [lit[0x3eb0],1,1] in writes and [lit[0x3eb4],4,640] in writes
  assert [w for w in writes if w[0]==lit[0x3eb8]+64]==[[lit[0x3eb8]+64,4,1],[lit[0x3eb8]+64,4,2]]
  assert calls[-2]['args'][0]==lit[0x3ebc] and calls[-1]['args'][:2]==[lit[0x3ec0],lit[0x3ebc]]
 assert int.from_bytes(u.mem_read(0x20000f38,4),'little')==0x20000850
 rows.append(dict(failure=failure,stop_pc=u.reg_read(UC_ARM_REG_PC),calls=calls,writes=writes,pcs=pcs,primask=u.reg_read(UC_ARM_REG_PRIMASK)))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text("# Application prefix with actual status/list insertion\n\nThis supplied application-entry fixture preloads the exact964-byte initialized-data span from originalflash B58C..B950 into RAM200004C0..20000884, matching separately verified reset. It executes actual4650,4634 andA3B0, replacing only44C4's hardware initialization dependency. The original descriptor at20000850 has callbackA1C1, classbyte1, requiredword20000CCC andpriorityFF; actualA3B0 inserts it into initially zero headslot20000F38 and returns1. Actual4634 consequently returnszero and the application bypasses its breakpoint.\n\nRemaining prefix calls are controlled as in1193. The original instruction sequence reaches3D50, stores its startupvalues and enablesinterrupts. The copied descriptor and head relation are asserted, rather than supplying A3B0's return. Physical initialization, listconcurrency, applicationloop and activeinterruptdelivery remain unresolved. This is a supplied RAMprecondition matchingreset, not a full boot replay. No canonicaladmission orCimplementation.\n");(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),literals={hex(a):hex(v) for a,v in lit.items()},files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS startup success and breakpoint-reach prefixes')
