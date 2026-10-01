from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('/Users/kalani/Repo/evenRealities-openCFW/reviews/P2-touch-calibration-setup-independent-review-1510/001/run');o.mkdir(parents=True,exist_ok=True);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();L={a:struct.unpack_from('<I',d,a-0x3300)[0] for a in [0x6974,0x6978,0x697c]};rows=[]
for old,status in itertools.product([0,0xa5a5a5a5,0xffffffff],[0,7,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0x40000000,0x10000);u.mem_map(0x09000000,0x1000);D=0x20002000;F=0x20002100;X=0x20002200;S=0x20002300;P=0x40000000
 for a,v in [(D,F),(F+8,X),(X,P),(P,old),(P+L[0x697c],old)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(S,bytes([0xa5])*24);u.reg_write(UC_ARM_REG_R0,S);u.reg_write(UC_ARM_REG_R1,D);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x9178:calls.append([u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a>=P else None);u.emu_start(0x6929,0,count=100)
 expected=[[P,4,old|0x80000000],[P+0x120,4,L[0x6974]],[P+0x100,4,L[0x6978]],[P+L[0x697c],4,old|6],[P+L[0x697c],4,old|7],[P+0x3800,4,1]]
 assert writes==expected and calls==[[P,6,S]] and bytes(u.mem_read(S,24))==bytes([0xa5])*24 and u.reg_read(UC_ARM_REG_R0)==status and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(old=old,status=status,writes=writes,calls=calls))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Calibration setup at 6928\n\nThe74-byte body [6928,6972) is followed by alignment and three literals. Resolve peripheral base through descriptor word0, configuration word8, then word0. Set control bit31. Write literal values to offsets120 and100, reading each back. Call9178(peripheral,6,inputScratchPointer). OR6 into the word at literal offset3034, reread and OR1, then write1 at3800. Return the helper status unchanged and restore frame.\n\nNine original-instruction fixtures check all six ordered MMIO writes, helper arguments, returned status, unchanged scratch under the explicit no-write helper control, and frame. 9178 effects andphysicalperipheral behavior remain unresolved; MMIO is synthetic. No canonical admission or C implementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literals=L,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
