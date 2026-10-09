from pathlib import Path
import itertools,json,hashlib,struct
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];p=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';rows=[]
for typ,fail,skip,sequence in itertools.product([0,1],[-1,0,1,2],[0,1,2,4,8],[(1,2),(4,8)]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x20000);u.mem_write(0x3300,b[32:]);u.mem_map(0x20000000,0x2000);nodes=[0x20001000+32*i for i in range(3)];events=[];returns=[]
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 w(0x20000f34+4*typ,nodes[0]);w(0x20000f24,0);w(0x20000f28+4*typ,0)
 for i,n in enumerate(nodes):
  params=0x20001200+8*i;w(params,0xaaaa0000+i,0xbbbb0000+i);w(n,0x1001+16*i,typ,skip if i==1 else 0,params,nodes[i-1] if i else 0,nodes[i+1] if i<2 else 0)
 def hook(uc,pc,size,_):
  if pc==0x2000:returns.append(uc.reg_read(UC_ARM_REG_R0));uc.emu_stop();return
  if pc in [0x1000,0x1010,0x1020]:
   i=(pc-0x1000)//16;ptr=uc.reg_read(UC_ARM_REG_R0);mode=uc.reg_read(UC_ARM_REG_R1);params=list(struct.unpack('<II',bytes(uc.mem_read(ptr,8))));assert params==[0xaaaa0000+i,0xbbbb0000+i];events.append([i,mode]);uc.reg_write(UC_ARM_REG_R0,0x4200ff if i==fail else 0);uc.reg_write(UC_ARM_REG_PC,uc.reg_read(UC_ARM_REG_LR))
 u.hook_add(UC_HOOK_CODE,hook)
 for mode in sequence:
  u.reg_write(UC_ARM_REG_R0,typ);u.reg_write(UC_ARM_REG_R1,mode);u.reg_write(UC_ARM_REG_SP,0x20001ff0);u.reg_write(UC_ARM_REG_LR,0x2001);before=len(returns);u.emu_start(0xa445,0,count=10000);assert len(returns)==before+1
 expected=[];last=None
 for i in range(3):
  if i==1 and skip&sequence[0]:continue
  expected.append([i,sequence[0]]);last=i
  if sequence[0]==1 and i==fail:break
 backwards=range((last if last is not None else 0)-1,-1,-1) if sequence[1]==2 else range(2,-1,-1)
 for i in backwards:
  if i==1 and skip&sequence[1]:continue
  expected.append([i,sequence[1]])
 assert events==expected,(typ,fail,skip,sequence,events,expected)
 failed=struct.unpack('<I',bytes(u.mem_read(0x20000f28+4*typ,4)))[0];expected_failed=nodes[fail] if sequence[0]==1 and fail>=0 and [fail,1] in events else 0;assert failed==expected_failed
 rows.append({'type':typ,'failure_callback':fail,'middle_skip_mask':skip,'sequence':sequence,'events':events,'returns':returns,'failed_callback':hex(failed),'last_executed':hex(struct.unpack('<I',bytes(u.mem_read(0x20000f24,4)))[0])})
(O/'pm-original-results.json').write_text(json.dumps({'cases':len(rows),'status':'PASS','stock_sha256':hashlib.sha256(b).hexdigest(),'results':rows,'limits':'Original dispatcher with coherent synthetic list and explicit callback-return providers. Proves selected ordering/skip/failure state, not physical sleep, IRQs, real callback internals or concurrency.'},indent=2)+'\n');print('PM original cases PASS',len(rows))
