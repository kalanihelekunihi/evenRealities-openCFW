from pathlib import Path
import hashlib,json,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-resource-flag-acquire-independent-review-1367/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();word=lambda a:struct.unpack_from('<I',d,a-0x3300)[0];invalid=word(0x8fc8);busy=word(0x8fcc);rows=[]
for base,owner,pointer,old in itertools.product([0,0x40250000],[0,2,256],[0,0x20002000],[0,1,255]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002000,bytes([old]));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_LR,0x09000001)
 for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],[base,owner,pointer]):u.reg_write(r,v)
 writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&255]));u.emu_start(0x8fa1,0,count=50)
 bad=not base or not owner or not pointer;ret=invalid if bad else (busy if old else 0);expected=[] if bad or old else [[pointer,1,owner&255]]
 assert writes==expected and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_PC)==0x09000000
 rows.append(dict(base=base,owner=owner,pointer=pointer,old=old,return_value=ret,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch resource flag acquisition 8FA0

Body8FA0..8FC8 is40 instruction bytes, followed by two errorliterals. Require nonzeroR0,R1,R2 in thatorder orreturn invalidliteral. Freshlyload byte atR2; nonzero returnsbusyliteral. Otherwise store lowbyte ofR1 atR2 andreturnzero. R0's pointedresource is notdereferenced; it is onlycheckednonnull. No interruptmasking,frame or atomicoperation occurs.

Receipt-derived originalinstruction fixtures include zero/nonzeroarguments, busyflags and owner256, which passesnonnullguard butstoreszero. Exactflagwrites andreturns matchindependentmodel. Realresourceeffects,atomicity andpointervalidity remainunresolved. No canonicaladmission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),errors=dict(invalid=invalid,busy=busy),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
