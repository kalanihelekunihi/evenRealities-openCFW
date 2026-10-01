from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-activation-success-path-independent-review-1378/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for budget,failures,old in itertools.product([0,1,3],[0,1,4],[0,0xa5a5a5a5]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000)
 for a,v in [(0x20002000,0x20002200),(0x20002004,0x40250000),(0x20002008,0x20002100),(0x20002200,48000000)]:u.mem_write(a,v.to_bytes(4,'little'))
 u.mem_map(0x40250000,0x1000);u.mem_write(0x40250008,old.to_bytes(4,'little'));u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);u.reg_write(UC_ARM_REG_R0,0x20002000);calls=[];writes=[];poll=[0];rets={0x6ac0:0xffffffff,0x4abe:0,0x5ca2:1,0x7bb8:2,0x5c7a:8,0x5fa4:budget,0x5c02:0xffffffff,0x4f54:0xffffffff,0x4e1c:0xffffffff}
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in rets or p==0x5c8e:
   args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]];calls.append([p,args])
   if p==0x5c8e:ret=int(poll[0]<failures);poll[0]+=1
   else:ret=rets[p]
   u.reg_write(UC_ARM_REG_R0,ret);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:writes.append([a,s,v&((1<<(8*s))-1)]) if a<0x2000e000 or a>=0x40000000 else None);u.emu_start(0x4af5,0,count=500)
 timedout=failures>budget;n=min(failures+1,budget+1);expected_calls=[0x6ac0,0x4abe,0x5ca2,0x7bb8,0x5c7a,0x5fa4]+[0x5c8e]*n+[0x6ac0]+[0x5c02]*3+[0x4f54,0x4e1c]
 assert [c[0] for c in calls]==expected_calls and next(c[1] for c in calls if c[0]==0x5fa4)==[1000000,48,5]
 assert [c[1][:2] for c in calls if c[0]==0x5c02]==[[i,0x20002000] for i in range(3)]
 assert writes==[[0x40250008,4,old|0x8000],[0x20002176,1,0],[0x20002176,1,1],[0x40250008,4,old&0xffff7fff]] and u.reg_read(UC_ARM_REG_R0)==(4 if timedout else 11) and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000
 rows.append(dict(budget=budget,failures=failures,old=old,timedout=timedout,calls=calls,writes=writes))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch activation success path 4AF4

On zero4ABE status, call5CA2,7BB8,5C7A withdescriptor, OR their rawresults into accumulatedstatus. ActualA6C0 divides descriptorword0's firstword by1000000. Call5FA4(1000000,quotient,5), retaining its return as retrycounter. Repeatedly call5C8E(descriptor): zero ends polling; nonzero with counterzero sets accumulatedstatus4 andends; otherwise decrementcounter andretry. Thus atmostcounter+1 polls occur, and zero on the last permitted poll succeeds.

Set contextbyte76one; call6AC0(1,descriptor),ignore result. Call5C02(index,descriptor) forindices0,1,2,ignore eachreturn. Continue common cleanup4F54/4E1C and freshperipheralbit15clear, then returnaccumulatedstatus. Six-word frame restored. Full localbody4AF4..4BA0 is172instructionbytes, followed byliterals.

Eighteen originalinstruction fixtures vary three retrybudgets, three failureprefixlengths andtworegisterpatterns. All deeperhelpers arecontrolled; unsigneddivision executesdirectly. Exactcallsequence,budgetarguments,cleanupwrites,flag,result andSP arechecked. Physicalpolltiming,helperbehavior andconcurrentmutation remainunresolved. No canonicaladmission orCimplementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
