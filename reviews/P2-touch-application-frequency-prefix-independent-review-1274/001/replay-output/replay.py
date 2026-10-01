from pathlib import Path
import json,hashlib,struct
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-application-frequency-prefix-independent-review-1274/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();lit={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in range(0x3ea4,0x3ec4,4)};rows=[]
for failure in [0]:
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x200004c0,d[0x828c:0x8650]);u.mem_map(0x40000000,0x100000);u.mem_map(0x40100000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_PRIMASK,1);calls=[];writes=[];pcs=[]
 driver_calls=[0x45d0,0xa148,0x9fd4,0xa104,0xa148,0xa01c,0xa104,0xa148,0xa01c,0xa104,0xa0bc]+[0x8ee4]*6+[0x45a4]
 driver_calls=[x for x in driver_calls if x not in [0xa148,0xa104,0x9fd4,0xa01c,0xa0bc]]
 driver_calls=[0xa33c,0x9c80,0x9f44,0x4734,0xa188,0x9c80,0x9f44,0xa33c,0x4734]
 driver_calls=[x for x in driver_calls if x not in [0xa33c,0x4734]]
 targets=driver_calls+[0x3638,0x3ee0,0x395c,0x3658,0x3ca4,0x3678,0x38e0,0x5dd8,0x5d90]
 def code(u,p,s,x):
  pcs.append(p)
  if p in [0x3cc6,0x3d50]:u.emu_stop();return
  if p in targets:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]];calls.append(dict(pc=p,args=args));u.reg_write(UC_ARM_REG_R0,failure if p==0x44c4 else 0);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]));u.emu_start(0x3cb5,0,count=5000)
 assert u.reg_read(UC_ARM_REG_SP)==0x2000eff8
 if failure:assert u.reg_read(UC_ARM_REG_PC)==0x3cc6 and [x['pc'] for x in calls]==targets[:2] and u.reg_read(UC_ARM_REG_PRIMASK)==1
 else:
  assert u.reg_read(UC_ARM_REG_PC)==0x3d50 and [x['pc'] for x in calls]==targets and u.reg_read(UC_ARM_REG_PRIMASK)==0
  assert next(c for c in calls if c['pc']==0x3ee0)['args'][:3]==[lit[0x3eac],lit[0x3ea8],lit[0x3ea4]]
  assert [lit[0x3eb0],1,1] in writes and [lit[0x3eb4],4,640] in writes
  assert [w for w in writes if w[0]==lit[0x3eb8]+64][-2:]==[[lit[0x3eb8]+64,4,1],[lit[0x3eb8]+64,4,2]]
  assert calls[-2]['args'][0]==lit[0x3ebc] and calls[-1]['args'][:2]==[lit[0x3ec0],lit[0x3ebc]]
 assert int.from_bytes(u.mem_read(0x20000f38,4),'little')==0x20000850
 assert [w for w in writes if w[0]==0x40010104]==[[0x40010104,4,65]]
 for address in [0x40010400,0x40010500]:assert [w for w in writes if w[0]==address]==[[address,4,0x3300],[address,4,0x3318]]
 assert [w for w in writes if w[0]==0x40010304]==[[0x40010304,4,0x300]]
 assert [w for w in writes if w[0]==0x40010000]==[[0x40010000,4,v] for v in [0x40000041,0x8000ff41,0x40000080,0x8000ff80,0x400000c0,0x8000ffc0]]
 rows.append(dict(failure=failure,stop_pc=u.reg_read(UC_ARM_REG_PC),calls=calls,writes=writes,pcs=pcs,primask=u.reg_read(UC_ARM_REG_PRIMASK)))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');assert int.from_bytes(u.mem_read(0x20000878,4),'little')==24000000
assert int.from_bytes(u.mem_read(0x20000874,4),'little')==24000
assert u.mem_read(0x20000870,1)==bytes([24])
assert int.from_bytes(u.mem_read(0x2000086c,4),'little')==((24000<<15)&0xffffffff)
(o/'pseudocode.md').write_text('# Application prefix with actual frequency derivation\n\nThis bounded fixture executes the original clock source, divider and frequency-state chain within the application initialization prefix. Both calls to 4734 execute 46F8, 9F9C, 9F34, the selected 9C44 source and A6C0 unsigned division. With synthetic trim zero, source selector zero and enabled bit 31, the original code derives 24,000,000; final RAM frequency is 24,000,000, ceiling MHz is 24, ceiling kHz is 24,000, and scaled kHz is 24,000 shifted left 15 modulo 2^32.\n\nOnly five clock calls remain controlled: 9C80, 9F44, A188, 9C80, 9F44. Later application dependencies remain controlled. All previously checked register writes, descriptor insertion, interrupt enabling and arrival at 3D50 are retained. RAM initialized data is copied from the authenticated source. Synthetic peripheral state establishes bounded instruction behavior; physical timing, concurrent register changes and the application loop remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),literals={hex(a):hex(v) for a,v in lit.items()},files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS startup success and breakpoint-reach prefixes')
