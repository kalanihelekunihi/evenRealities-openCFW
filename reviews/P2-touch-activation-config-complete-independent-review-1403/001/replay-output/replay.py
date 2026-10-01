from pathlib import Path
import json,hashlib,struct,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-activation-config-complete-independent-review-1403/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();literal=struct.unpack_from('<I',d,0x7284-0x3300)[0];rows=[]
for astatus,bstatus,fill,state1,state2,enabled in itertools.product([0,1,0xffffffff],[0,2,0xffffffff],[0,0xa5,0xff],[0,4],[0,8],[0,1]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000)
 for a,v in [(0x20002000,0x20002100),(0x20002008,0x20002200),(0x2000201c,0x20002300)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_write(0x20002129,bytes([1,2,3]));u.mem_write(0x20002200,bytes([fill])*0x80);u.mem_write(0x20002214,bytes(4));u.mem_write(0x20002224,(0x20002400).to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_R0,0x20002000);calls=[];writes=[];rets={0x6384:astatus,0x5378:bstatus,0x56a4:0xffffffff,0x5d70:0x12345678}
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in rets or p in [0x6ac0,0x7064,0x7dde,0x5cac]:calls.append([p,u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]);u.reg_write(UC_ARM_REG_R0,rets[p] if p in rets else (state1 if p==0x6ac0 and calls[-1][1]==1 else state2 if p==0x6ac0 else 16 if p==0x7064 else enabled if p==0x7dde else 32));u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&((1<<(8*s))-1)]) if a<0x2000e000 else None);u.emu_start(0x71c9,0,count=200)
 assert [c[0] for c in calls[:5]]==[0x6384,0x5378,0x56a4,0x56a4,0x5d70] and calls[2:4]==[[0x56a4,0,0x20002000],[0x56a4,1,0x20002000]] and calls[4]==[0x5d70,0x20002400,0x20002000]
 assert writes==[[0x20002315,1,0],[0x20002252,1,0],[0x20002274,1,1],[0x20002275,1,2],[0x2000224c,1,3],[0x20002210,4,literal],[0x20002228,4,0x12345678]] 
 ret=astatus|bstatus;expected_extra=[]
 if not ret:
  expected_extra.append([0x6ac0,1,0x20002000]);ret|=state1
  if not ret:
   expected_extra.append([0x6ac0,2,0x20002000]);ret|=state2
   if not ret:expected_extra.append([0x7064,0x20002000,0x20002000]);ret=16
 for i in range(3):
  expected_extra.append([0x7dde,i,0x20002000])
  if enabled:expected_extra.append([0x5cac,i,0x20002000]);ret|=32
 assert [c[:2] for c in calls[5:]]==[c[:2] for c in expected_extra] and u.reg_read(UC_ARM_REG_R0)==ret and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(state1=state1,state2=state2,enabled=enabled,return_value=ret,first_status=astatus,second_status=bstatus,fill=fill,calls=calls,writes=writes,retained_status=astatus|bstatus))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('# Touch activation configuration complete local flow\n\nBody71C8..7284 is188 instructionbytes,followed byliteral. Initialcopy/callbackprefix isdocumented in1398. Ifaccumulated6384/5378status iszero,call6AC0(1,descriptor),ORresult. Ifstillzero,call6AC0(2,descriptor),ORresult. Ifstillzero,call7064(descriptor) andreplaceaccumulatedstatus withitsreturn. Thenforeachindex0,1,2 call7DDE(index,descriptor); ifnonzero,call5CAC(index,descriptor) andORreturn. Returnaccumulatedstatus,restorefour-wordframe.\n\nReceipt-derived originalinstruction fixtures extend1398 throughreturn,varyingfirststatuses,twostatecallstatuses andall-rowenableflag. Deeperhelpers controlled;nullcallback supplied. Exactcopywrites,reachedcallsequence,returnedstatus andSP checked. Callbacknonnullbehavior,realhelpercontracts andphysicalactivation remainunresolved. No canonicaladmission orCimplementation.\n');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),literal=literal,files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
