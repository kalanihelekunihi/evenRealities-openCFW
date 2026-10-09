from pathlib import Path
import itertools,json,hashlib
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];p=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
rows=[]
for entry,n,d in itertools.product([0xa6c0,0xa7cc],[0,1,2,3,0x7fffffff,0x80000000,0xffffffff],[0,1,2,3,0x7fffffff,0x80000000,0xffffffff]):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x20000);u.mem_write(0x3300,b[32:]);u.mem_map(0x20000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x20000ff0);u.reg_write(UC_ARM_REG_LR,0x2001);u.reg_write(UC_ARM_REG_R0,n);u.reg_write(UC_ARM_REG_R1,d);returns=[];zero_calls=[]
 def hook(uc,pc,size,_):
  if pc==0x2000:returns.append(True);uc.emu_stop()
  if pc==0xa9a8:zero_calls.append(uc.reg_read(UC_ARM_REG_R0))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry|1,0,count=10000);assert returns
 q=u.reg_read(UC_ARM_REG_R0);rem=u.reg_read(UC_ARM_REG_R1)
 if d:
  assert q==n//d
  if entry==0xa7cc:assert rem==n%d
 rows.append({'entry':hex(entry),'dividend':n,'divisor':d,'r0':q,'r1':rem,'zero_hook_inputs':zero_calls,'normal_arithmetic_verified':bool(d)})
(O/'original-results.json').write_text(json.dumps({'cases':len(rows),'normal_arithmetic_cases':sum(bool(x['divisor']) for x in rows),'stock_sha256':hashlib.sha256(b).hexdigest(),'results':rows,'limits':'Synthetic register/stack input, real stock instructions and real stock divide-zero hook; no exception/physical device behavior. Zero outputs observed, not compared to undefined C division semantics.'},indent=2)+'\n')
print('original cases',len(rows),'zero observations',[(x['dividend'],x['r0'],x['r1']) for x in rows if x['entry']=='0xa7cc' and not x['divisor']])
