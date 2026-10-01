from pathlib import Path
import json,hashlib,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-pin-config-8ee4-independent-review-1231/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda v:hashlib.sha256(v).hexdigest();rows=[];P=0x40040000;C=0x20001000
for pin,flag0,flag1,old in itertools.product([0,7],[0,1],[0,1],[0,0xffffffff,0xa5a5a5a5]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);u.mem_map(P,0x1000);u.mem_map(0x09000000,0x1000);u.mem_write(P+8,old.to_bytes(4,'little'))
 values=[1,15,15,3,flag0,flag1]
 for i,v in enumerate(values):u.mem_write(C+4*i,v.to_bytes(4,'little'))
 for r,v in [(UC_ARM_REG_R0,P),(UC_ARM_REG_R1,pin),(UC_ARM_REG_R2,C),(UC_ARM_REG_SP,0x2000f000),(UC_ARM_REG_LR,0x09000001)]:u.reg_write(r,v)
 calls=[];writes=[];helpers=[0x8e64,0x8e84,0x8e28,0x8ebe]
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in helpers:
   calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1),u.reg_read(UC_ARM_REG_R2)]);u.reg_write(UC_ARM_REG_R0,0xffffffff);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,p,s,v,x:writes.append([p,s,v]) if p>=0x40000000 else None);u.emu_start(0x8ee5,0,count=300)
 first=(old&~(1<<24))|(flag0<<24);second=(first&~(1<<25))|(flag1<<25)
 assert calls==[[a,P,pin,v] for a,v in zip(helpers,values[:4])] and writes==[[P+8,4,first],[P+8,4,second]]
 assert u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_R0)==0 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(pin=pin,flags=[flag0,flag1],initial_word=old,calls=calls,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch pin configuration valid paths

The body8EE4..8F92 rejects null base or null configuration with005A0001. Nonnull paths contain BKPT1 checks for pin>7 and configuration fields beyond their bounds: u32+0<=1, u32+4<=15, byte+8<=15, u32+12<=3, u32+16<=1 andu32+20<=1. Breakpoint continuation is not modeled as input rejection.

Valid paths call8E64(base,pin,u32+0),8E84(base,pin,u32+4),8E28(base,pin,byte+8),8EBE(base,pin,u32+12). Each raw helper return is ignored. The last two fields are checked again after these calls. Fresh reads of base+8 update bit24 from field+16, store, then freshly read again and updatebit25 fromfield+20 andstore. Returnzero and restore16-byteframe. Helpermutation ofconfiguration orMMIO may affect these laterfreshloads.

Twenty-four original-instruction valid-path fixtures check both pin boundaries, both flags and three initialregisterpatterns. The four helpers are controlled to returnFFFFFFFF without memoryeffects, demonstrating ignoredstatus only under that contract. Null andbreakpoint paths are staticevidence, dynamicallyuntestedhere. Physicalregisterbehavior,breakpointsemantics andhelpercontracts remain unresolved. No canonical admission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),runtime_span=[0x8ee4,0x8f92],fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows),'pin configurations')
