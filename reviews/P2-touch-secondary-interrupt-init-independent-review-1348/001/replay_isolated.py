from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-secondary-interrupt-init-independent-review-1348/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for status,relocated in itertools.product([0,1,0xffffffff],[0,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x1000);u.mem_write(0xe000ed08,(0x20000400 if relocated else 0).to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in [0x4c7c,0x4af4]:calls.append([p,u.reg_read(UC_ARM_REG_R0)]);u.reg_write(UC_ARM_REG_R0,status if p==0x4c7c else 0x12345678);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a<0x2000e000 or a>=0xe0000000 else None);u.emu_start(0x38e1,0,count=300)
 expected=[] if status else [[0xe000e408,4,192]]+([[0x20000460,4,0x3949]] if relocated else [])+[[0xe000e280,4,256],[0xe000e100,4,256]]
 assert writes==expected and calls==[[0x4c7c,0x200004ec]]+([[0x4af4,0x200004ec]] if not status else [])
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_R0)==(status if status else 0x12345678)
 rows.append(dict(initial_status=status,relocated=relocated,calls=calls,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch secondary interrupt initialization 38E0

Body38E0..3936 is86 instruction bytes, excluding NOP/pool. Copy original eight-byte descriptorB0F0 to local stack: signed halfword index8 and priorityword3. Call4C7C(200004EC); nonzero returns that status and restoresframe. Onzero call actualA2A8(stackdescriptor,3949), executing actualA214 and conditionallyA274. For nonnegative descriptor index, write1<<(index&31) toE000E280 andE000E100. Then call4AF4(200004EC), restoreframe and return its raw result. Signed-negative localbranches are present but original copieddescriptor hasindex8.

Six originalinstruction fixtures cover three controlled firststatuses and bothVTORstates. Two deeperhelpers are controlled; interruptregistrationhelpers executeactualinstructions. Exactpriority/vector/enablewrites, reachedcalls/rawreturn andSP are checked. Copieddescriptor mutation, physicalinterruptdispatch and deeperhelperbehavior remainunresolved. No canonicaladmission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
