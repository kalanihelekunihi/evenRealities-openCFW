from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-calibration-acquisition-independent-review-1506/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[];L={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in [0x7cf0,0x7cf4]}
for raw,n,flags,mode,mult,done in itertools.product([0,1,65535],[0,1,15],[0,2],[0,1,10],[0,1,255],[0,1,0xffffffff]):
 status=0
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=0x20002100;X=0x20002200;T=0x20002300;R=0x20002500;O=0x20002700;OUT=0x20002900;sp=0x2000f000
 for a,v in [(D,F),(F+8,X),(X,0x40000000),(D+12,T),(D+16,R),(D+40,O)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(T+122,bytes([mode]));u.mem_write(T+132,bytes([mult]));u.mem_write(R+33,bytes([flags]));u.mem_write(O+20,(n<<16).to_bytes(4,'little'));u.mem_write(0x40003200,raw.to_bytes(4,'little'));u.mem_write(0x40000000,(0x87654321).to_bytes(4,'little'));u.mem_write(sp,D.to_bytes(4,'little'));u.reg_write(UC_ARM_REG_R0,OUT);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_R2,0);u.reg_write(UC_ARM_REG_R3,0);u.reg_write(UC_ARM_REG_SP,sp);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x6ac0,0x6928,0x7288,0x6980]:
   calls.append([p]+[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]);u.reg_write(UC_ARM_REG_R0,0 if p==0x6ac0 else 99 if p==0x6928 else 88 if p==0x7288 else done);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x7bc1,0,count=300)
 adjustment=((n+4)>>2)*(96 if flags&3==2 else 2)
 if flags&3==2 and mode in [1,10] or (n+1)&1==0:adjustment=(adjustment-1)&0xffffffff
 product=((raw-adjustment)*mult)&0xffffffff;result=product if product<65536 else L[0x7cf4];result=result or 1
 assert int.from_bytes(u.mem_read(OUT,4),'little')==result and int.from_bytes(u.mem_read(0x40000000,4),'little')==0x07654321 and [c[:3] for c in calls]==[[0x6ac0,5,D],[0x6928,sp-64,D],[0x7288,0,0],[0x6980,88,D]] and calls[2][3]==D and u.reg_read(UC_ARM_REG_R0)==(0 if done else 4) and u.reg_read(UC_ARM_REG_SP)==sp and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(status=status,completion=done,returned_status=0 if done else 4,raw=raw,n=n,flags=flags,mode=mode,mult=mult,result=result))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Calibration acquisition branch at 7BC0\n\nExtend1503 with a zero state-helper result. Original7BC0 calls6928(scratch,descriptor), then7288(rowIndex,packetIndex,descriptor), then6980(previous R0,descriptor). Controlled returns99 and88 from the first two helpers demonstrate their flow: the first is discarded before7288; the second remains R0 entering6980. Nonzero6980 result leaves retained status0; zero adds errorbit4. The subsequent original hardware-read/output arithmetic and cleanup still execute for both results.\n\nThe486 original-instruction fixtures check the exact acquisition call order and arguments, retained status, output word, control-bit clear and restored frame. Helpers6AC0/6928/7288/6980 are controlled; MMIO is synthetic. Scratch/helper effects, record mode123==7 and physical behavior remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=L,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
