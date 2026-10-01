from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-activation-reset-helpers-independent-review-1391/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();mask=struct.unpack_from('<I',d,0x591c-0x3300)[0];rows=[]
for entry,old,status in itertools.product([0x58f8,0x7e04],[0,0xa5a5a5a5,0xffffffff],[0,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_write(0x20002004,(0x20002100).to_bytes(4,'little'));u.mem_write(0x20002100,old.to_bytes(4,'little')*8);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,0x20002000);calls=[];writes=[]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p==0x5868:calls.append([u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,status);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v]) if a<0x2000e000 else None);u.emu_start(entry|1,0,count=100)
 if entry==0x58f8:assert calls==[[i,0x20002000] for i in [2,1,0]] and writes==[[0x20002108,4,old&mask]] and u.reg_read(UC_ARM_REG_R0)==status
 else:assert not calls and writes==[[0x20002102,2,0],[0x20002106,1,0],[0x20002116,2,0],[0x2000211c,1,0]] and u.reg_read(UC_ARM_REG_R0)==0x20002000
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(entry=entry,old=old,controlled_status=status,calls=calls,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch activation reset helpers

58F8..591C is36 instructionbytes, followed bymaskliteral. Freshlyload descriptor+4pointer/word8,ANDmask/store. Call5868(index,descriptor) forindices2,1,0 inthatorder, ignoringearlierreturns andreturninglastcall's rawR0. Restorefour-wordframe. 7E04..7E14 is16instructionbytes: freshlyload descriptor+4pointer,clearhalfwords2/16 andbytes6/1C inthatorder,return throughLR preservingincomingR0. No frame orhelpercalls occur there.

Twelve originalinstruction fixtures coverbothentries, threeoldpatterns andtwo controlled5868statuses. Exactcalls,writes,returns andSP matchindependentmodel. Pointervalidity,real5868behavior andconcurrency remainunresolved. No canonicaladmission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),mask=mask,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
