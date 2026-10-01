from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-packet-init-local-independent-review-1484/001');o.mkdir(parents=True,exist_ok=True);src=o/'touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for group,index,mode,fill,status in itertools.product([0,1],[0,1],[0,1],[0,1,255],[1,7]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;C=0x20002100;T=0x20002200;R=0x20002400;I=0x20002500;O=0x20002600
 for off,v in [(8,C),(12,T),(16,R),(48,I),(52,I)]:u.mem_write(D+off,v.to_bytes(4,'little'))
 for a,size in [(C,128),(T,144),(R,60)]:u.mem_write(a,bytes([fill])*size)
 u.mem_write(T+122,bytes([mode]));u.mem_write(O,bytes([0xa5])*48);u.reg_write(UC_ARM_REG_R0,group);u.reg_write(UC_ARM_REG_R1,index);u.reg_write(UC_ARM_REG_R2,O);u.reg_write(UC_ARM_REG_R3,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x51bc:calls.append([p]+[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.emu_start(0x5549,0,count=300)
 half=fill*257;expected=bytearray([0xa5]*48);put=lambda off,v:expected.__setitem__(slice(off,off+4),(v&0xffffffff).to_bytes(4,'little'));base=20 if group else 0
 if group:
  put(0,(fill&15)|((fill<<4)&255)|((fill<<8)&0xf00)|((half<<16)&0x3f0000)|(fill<<24));put(4,half|(half<<16));put(8,half|((fill<<16)&0x70000)|(0 if mode==1 else 0x1000000));put(12,0);put(16,0)
 else:put(24,fill<<24)
 val=(((fill-1)<<14)&0x4000)|((half-1)&0x3fff)
 if fill==1 and half!=index:val|=0x8000
 put(base+12,val)
 assert bytes(u.mem_read(O,48))==expected and calls==[[0x51bc,I+4*index,O+base,D]] and u.reg_read(UC_ARM_REG_R0)==status and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(group=group,index=index,mode=mode,fill=fill,status=status,output=expected.hex(),calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Packet initialization local writes at 5548\n\nThe code body [5548,569E) is 342 bytes, followed by alignment and a mask literal. Select index table descriptor word +48 for group zero, +52 otherwise. Its first halfword selects the stride-144 record and stride-60 row configuration. Group1 packs context/row fields into five leading output words, then advances output20 bytes. Group0 writes record byte +140 into output word +24 high byte. Both pack decremented record byte +132 and decremented row halfword +44 into output word +12. When row byte +52 equals1 and record halfword +128 differs from index, OR32768 into that word.\n\nCall51BC(indexPair,adjustedOutput,descriptor). A nonzero result returns immediately. The 48 fixtures cover both groups, indices, record modes and source fills with nonzero controlled helper statuses, checking all48 outputbytes and frame. The zero-result branch and 5528 dependency remain unresolved; physical meanings and independent-field variation remain open. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
