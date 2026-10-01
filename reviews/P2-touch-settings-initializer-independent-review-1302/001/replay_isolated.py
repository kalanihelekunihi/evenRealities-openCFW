from pathlib import Path
import hashlib,json,itertools
from unicorn import *
from unicorn.arm_const import *
b=Path('g2/build/pseudocode-first/20260930T190500Z');o=Path('reviews/P2-touch-settings-initializer-independent-review-1302/001/replay-output');o.mkdir(parents=True,exist_ok=False);src=b/'attempts/P2-touch-reset-pseudocode-108/001/touch.flash.bin';d=src.read_bytes();h=lambda x:hashlib.sha256(x).hexdigest();rows=[]
for init,read,magic,timeout,erase,write in itertools.product([0,1],repeat=6):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x10000);u.mem_write(0x3300,d);u.mem_map(0x20000000,0x10000);original=(0x45564e55 if magic else 0x11223344).to_bytes(4,'little')+(123).to_bytes(2,'little')+(7 if timeout else 0).to_bytes(2,'little');u.mem_write(0x200009d0,original);u.mem_map(0x09000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x2000f000);u.reg_write(UC_ARM_REG_LR,0x09000001);calls=[];stores=[];rets={0x34d8:init,0x3520:read,0x35b0:erase,0x3568:write,0xa2f0:0}
 def code(u,p,s,x):
  if p==0x09000000:u.emu_stop()
  elif p in rets:
   calls.append(dict(pc=p,args=[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2]]));u.reg_write(UC_ARM_REG_R0,rets[p]);u.reg_write(UC_ARM_REG_PC,u.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,code);u.hook_add(UC_HOOK_MEM_WRITE,lambda u,t,a,s,v,x:stores.append([a,s,v&((1<<(8*s))-1)]) if 0x200009d0<=a<0x200009d8 else None);u.emu_start(0x395d,0,count=300)
 expected_calls=[0x34d8];expected_stores=[]
 if not init:
  expected_calls+=[0x3520]
  if not read and magic:
   if not timeout:expected_stores=[[0x200009d6,2,1000]]
  else:
   expected_calls+=[0x35b0]
   if not erase:expected_calls+=[0xa2f0,0x3568];expected_stores=[[0x200009d0,4,0x45564e55],[0x200009d4,2,0],[0x200009d6,2,1000]]
 assert [c['pc'] for c in calls]==expected_calls and stores==expected_stores and u.reg_read(UC_ARM_REG_PC)==0x09000000 and u.reg_read(UC_ARM_REG_SP)==0x2000f000 and u.reg_read(UC_ARM_REG_R0)==0
 for c in calls:
  if c['pc'] in [0x3520,0x3568]:assert c['args']==[0,0x200009d0,8]
  if c['pc']==0xa2f0:assert c['args'][0]==10
 rows.append(dict(init_status=init,read_status=read,magic_matches=magic,timeout_nonzero=timeout,erase_status=erase,write_status=write,calls=calls,stores=stores))
(o/'replays.json').write_text(json.dumps(rows,indent=2)+'\n');(o/'pseudocode.md').write_text('''# Touch settings initializer 395C

Body 395C..39F8 is 156 instruction bytes, excluding its following literal pool. Call 34D8; nonzero status prints through actual zero-return 3EE0 and returns. Otherwise call 3520(0,200009D0,8). If read succeeds and the first word equals 45564E55, retain existing halfwords at offsets four/six, except replace a zero timeout at six with 1000. Print their values and return zero through 3EE0.

A failed read or mismatched magic prints and calls 35B0. On erase failure print and return zero. Otherwise call A2F0(10), set word magic 45564E55, halfword offset four zero, halfword offset six 1000, then call 3568(0,200009D0,8). Both write success and failure print and return zero. Original 3EE0 executes; five deeper helpers are controlled status boundaries. The procedure restores its frame on each branch.

Sixty-four original-instruction fixtures cover six binary preconditions/statuses, checking reached control sequence, read/write arguments, exact local object stores, return and frame. Controlled storage routines do not mutate memory; supplied object states are explicit. Storage functionality, physical delay and diagnostic output remain unresolved. No canonical admission or C implementation.
''');(o/'replay.py').write_bytes(Path(__file__).read_bytes());(o/'receipt.json').write_text(json.dumps(dict(source=dict(path=str(src),sha256=h(d)),fixtures=len(rows),files={p.name:h(p.read_bytes()) for p in sorted(o.iterdir())},accepted=False),indent=2)+'\n');print('PASS',len(rows))
