from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-packet-builder-original-mask-helper-independent-review-1480/001');o.mkdir(parents=True,exist_ok=True);src=o/'touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for group,mode117,mode116,rowmode,n,pin in itertools.product([0,1],[0,2,5],[0,2,4],[0,1,2],[0,1,2],[0,31,32]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=0x20002100;C=0x20002200;T=0x20002300;O=0x20002500;I=0x20002700
 for off,v in [(0,F),(8,C),(12,T),(20,0x20002900),(24,0x20002900),(40,O),(44,O),(48,I),(52,I)]:u.mem_write(D+off,v.to_bytes(4,'little'))
 for off,v in [(99,17),(100,31),(104,11),(106,13),(107,43),(109,59),(116,mode116),(117,mode117)]:u.mem_write(C+off,bytes([v]))
 u.mem_write(F+12,n.to_bytes(2,'little'));u.mem_write(F+44,bytes([n]));u.mem_write(0x20002800,(0x20002900).to_bytes(4,'little'));u.mem_write(0x20002805,bytes([n]));
 for j in range(n):u.mem_write(0x20002900+8*j+5,bytes([(pin+j)&255]))
 u.mem_write(T+122,bytes([rowmode]));u.mem_write(T+8,(0x20002800).to_bytes(4,'little'));u.reg_write(UC_ARM_REG_R0,group);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x5188:calls.append([p]+[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]])
  elif p==0x5548:calls.append([p]+[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2,UC_ARM_REG_R3]]);u.reg_write(UC_ARM_REG_R0,3);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x56a5,0,count=2000)
 count=4 if group else 5;stride=44 if group else 28;expected=[]
 firstmap=31 if mode117==2 else 59 if mode117==5 else 17;secondmap=31 if mode116==2 else 43 if mode116==4 else 17;mapping=secondmap if rowmode==1 else firstmap if rowmode==2 else 31
 mask=0
 for j in range(n):v=(pin+j)&255;mask|=(1<<v)&0xffffffff if v<32 else 0
 for i in range(count):
  dest=O+stride*i+(20 if group else 0);expected.extend([[0x5548,group,i,O+stride*i,D],[0x5188,mask,mapping,dest]])
  if n:expected.append([0x5188,mask,43 if rowmode==1 else mapping,dest])
  if rowmode==1:expected.append([0x5188,mask,11,dest])
 assert [c[:len(e)] for c,e in zip(calls,expected)]==expected and len(calls)==len(expected) and u.reg_read(UC_ARM_REG_R0)==mask and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 image=bytearray(512)
 for e in expected:
  if e[0]!=0x5188:continue
  _,bits,selection,dest=e
  for j in range(3):
   off=dest-O+4*j;old=int.from_bytes(image[off:off+4],'little');v=old|bits if selection&(4>>j) else old&(~bits&0xffffffff);image[off:off+4]=v.to_bytes(4,'little')
 assert bytes(u.mem_read(O,512))==image
 rows.append(dict(group=group,mode117=mode117,mode116=mode116,rowmode=rowmode,count=n,pin=pin,mask=mask,calls=calls,return_value=mask))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Packet builder with original mask output helper\n\nOriginal 56A4 executes original 5188 for all base, second-list and mode-1 subrecord calls. Only 5548 remains controlled and supplies no output writes. The 486 inherited nonempty-mask fixtures check exact helper-entry arguments and a separate whole-buffer model of every three-word mask update, including repeated writes to the same output row. Final R0 is the last mask, as preserved by original 5188.\n\nShared pin arrays, zero index halfwords and controlled 5548 constrain scope. Arbitrary nested indices, the remaining helper contract and physical meanings remain unresolved. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
