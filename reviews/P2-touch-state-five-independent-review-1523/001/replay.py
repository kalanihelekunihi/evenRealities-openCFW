from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-state-five-independent-review-1523/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();L={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in [0x6ab8,0x6abc]};rows=[]
for old,status in itertools.product([0,0xa5a5a5a5,0xffffffff],[0,7,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=0x20002100;X=0x20002200;S=0x20002300;P=0x40000000
 for a,v in [(D,F),(F+8,X),(X,P),(P,old),(P+0x400,old)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(S,bytes([0xa5])*24);u.reg_write(UC_ARM_REG_R0,D);u.reg_write(UC_ARM_REG_R1,0);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x685c:calls.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a>=P else None);u.emu_start(0x6a81,0,count=100)
 expected=[[P+0x400,4,0]]
 for i in range(3):expected.extend([[P+0x608+64*i,4,0x03000000],[P+L[0x6ab8]+64*i,4,L[0x6abc]]])
 assert writes==expected and calls[0][0]==D and len(calls)==1 and bytes(u.mem_read(S,24))==bytes([0xa5])*24 and u.reg_read(UC_ARM_REG_R0)==0x03000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(old=old,status=status,writes=writes,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# State-five preparation at 6A80\n\nThe56-byte body [6A80,6AB8) is followed by two literals. Resolve the peripheral through descriptor/configuration pointers, call685C(descriptor), then write0 to peripheral400. For three rows at64-byte stride, write03000000 at608 and literal00101000 at60C. The helper status is overwritten: return incidental03000000 inR0 and restore8-byte frame.\n\nNine original-instruction fixtures check seven orderedMMIOwrites, callargument, independence fromcontrolledhelperstatus, incidentalreturn andframe. 685C andphysicalhardware effects remain unresolved;MMIO is synthetic. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=L,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
