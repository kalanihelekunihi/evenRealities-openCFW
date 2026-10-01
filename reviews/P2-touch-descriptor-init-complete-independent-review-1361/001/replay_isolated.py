from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-descriptor-init-complete-independent-review-1361/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for flags,fill,first,second in itertools.product(itertools.product([0,0xa5,0xff],repeat=3),[0,0xa5,0xff],[0,1],[0,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,(0x20002400).to_bytes(4,'little'));u.mem_write(0x20002400,bytes(range(64)));u.mem_write(0x20002008,(0x20002100).to_bytes(4,'little')+(0x20002200).to_bytes(4,'little'));u.mem_write(0x20002200,(0x20002300).to_bytes(4,'little'));u.mem_write(0x20002100,bytes([fill])*0x80)
 for i,v in enumerate(flags):u.mem_write(0x20002323+i*0x3c,bytes([v]))
 u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_R0,0x20002000);writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x6ac0,0x4c72]:
   calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,first if p==0x6ac0 else second);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&((1<<(s*8))-1)]) if a<0x2000e000 else None);u.emu_start(0x4c7d,0,count=300)
 expected=[[0x20002174,1,0],[0x20002175,1,0]]+[[0x20002100+x,4,0] for x in [0,4,12,8]]+[[0x20002323+i*0x3c,1,v|6] for i,v in enumerate(flags)]
 word=lambda a:int.from_bytes(d[a-0x3300:a-0x3300+4],'little')
 expected += [[0x2000211c,4,0],[0x2000212c,4,word(0x4da8)],[0x20002114,4,0],[0x2000214c,1,0],[0x20002157,1,47],[0x20002158,1,45],[0x20002159,1,49],[0x20002130,2,0x1716],[0x20002132,2,0x1918],[0x20002153,1,52],[0x20002154,1,53],[0x2000213c,2,word(0x4dac)&65535],[0x2000214e,1,0],[0x2000214f,1,255],[0x20002150,1,142],[0x20002151,1,1]]
 for i,v in enumerate(flags):expected += [[0x20002323+i*0x3c,1,(v|6)|8],[0x20002323+i*0x3c,1,(v|6)|24]]
 expected += [[0x20002140,2,0x1f1e],[0x2000213e,2,0x1d1c],[0x20002144,2,0x2322],[0x20002142,2,0x2120]]+[[0x20002100+a,1,v] for a,v in [(0x72,1),(0x4d,3),(0x5a,1),(0x5b,0),(0x5c,0),(0x5d,6),(0x5e,4),(0x5f,10),(0x60,1)]]+[[0x20002124,4,word(0x4db0)],[0x2000214a,2,32]]
 assert writes==expected and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_R0)==(first if first else second)
 assert calls[0]==[0x6ac0,0,0x20002000] and len(calls)==(1 if first else 2)
 if not first:assert calls[1][0:2]==[0x4c72,0x20002000]
 rows.append(dict(first_status=first,second_status=second,calls=calls,initial_flags=flags,initial_fill=fill,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Touch descriptor initializer complete local paths\n\nThe nonnull body continues the previously recovered 1355/1358 operations. Copy config halfwords 1E→context40,1C→3E,22→44,20→42. Set context bytes72=1,4D=3,5A=1,5B=0,5C=0,5D=6,5E=4,5F=10,60=1. Store literal4DB0 at context24 and halfword32 at4A. Call6AC0(0,descriptor). Nonzero status restores six-word frame and returns that status; zero calls4C72(descriptor), restores frame and returns its raw result. Null descriptor returns1 through the same epilogue.\n\nFull local body4C7C..4DA8 is300 instruction bytes, excluding literal pool. Prior header/copy/row pseudocode remains in1355/1358; this packet extends their original-instruction fixtures through return. Two deeper helpers are controlled without memory effects. Receipt-derived fixtures vary three original rowflags/contextfill and both call statuses, checking every ordered store, reachedcall, result andSP. Rowhalfwords are suppliedzero; nonzero-row branches and nullentry are decoded but not fixture-covered here. Deeper behavior, invalid pointers and physical meaning remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
