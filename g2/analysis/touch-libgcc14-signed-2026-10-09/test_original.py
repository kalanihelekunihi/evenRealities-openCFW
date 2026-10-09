from pathlib import Path
import itertools,json,hashlib
from unicorn import Uc,UC_ARCH_ARM,UC_MODE_THUMB,UC_MODE_MCLASS,UC_HOOK_CODE
from unicorn.arm_const import *
O=Path(__file__).resolve().parent;R=O.parents[2];p=R/'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin';b=p.read_bytes();assert hashlib.sha256(b).hexdigest()=='0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d';rows=[]
values=[-2147483648,-2147483647,-3,-2,-1,0,1,2,3,2147483647]
for entry,n,d in itertools.product([0xa7d4,0xa9a0],values,values):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0,0x20000);u.mem_write(0x3300,b[32:]);u.mem_map(0x20000000,0x1000);u.reg_write(UC_ARM_REG_SP,0x20000ff0);u.reg_write(UC_ARM_REG_LR,0x2001);u.reg_write(UC_ARM_REG_R0,n&0xffffffff);u.reg_write(UC_ARM_REG_R1,d&0xffffffff);done=[];zeros=[]
 def hook(uc,pc,size,_):
  if pc==0x2000:done.append(True);uc.emu_stop()
  if pc==0xa9a8:zeros.append(uc.reg_read(UC_ARM_REG_R0))
 u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry|1,0,count=10000);assert done
 q=u.reg_read(UC_ARM_REG_R0);rem=u.reg_read(UC_ARM_REG_R1);overflow=n==-2147483648 and d==-1
 if d and not overflow:
  expected=(abs(n)//abs(d))*(-1 if (n<0)!=(d<0) else 1);assert q==expected&0xffffffff
  if entry==0xa9a0:assert rem==(n-expected*d)&0xffffffff
 rows.append({'entry':hex(entry),'dividend':n,'divisor':d,'r0':hex(q),'r1':hex(rem),'zero_hook_inputs':zeros,'C_undefined_overflow_case':overflow,'normal_arithmetic_verified':bool(d) and not overflow})
(O/'original-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'normal_arithmetic_cases':sum(x['normal_arithmetic_verified'] for x in rows),'results':rows,'limits':'Synthetic registers/stack, original stock body and real zero hook. Zero and MIN/-1 outputs are observations, not defined C arithmetic or hardware exception claims.'},indent=2)+'\n');print('signed original cases PASS',len(rows));print('exceptional observations',[(x['entry'],x['dividend'],x['divisor'],x['r0'],x['r1']) for x in rows if x['C_undefined_overflow_case'] or (not x['divisor'] and x['dividend'] in [-3,0,3])])
