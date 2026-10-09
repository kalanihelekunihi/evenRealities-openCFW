from pathlib import Path
import json,itertools,hashlib,struct
D=Path(__file__).resolve().parent
exec((D/'verify.py').read_text().split('for mutex,prefill,held,wait in itertools.product')[0])
def helper(native,kind,count=0,value=0,held=0,current_null=False):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,v):u.mem_write(a,struct.pack('<I',v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 w(Q+36,count);w(Q+48,WAITER);w(WAITER,value);w(0x20074a20,0 if current_null else CUR);w(CUR+100,held)
 observed=[]
 def guard(u,a,n,d):
  if native:assert 0x100000<=a<0x110000;observed.append(a)
 u.hook_add(UC_HOOK_CODE,guard);u.reg_write(UC_ARM_REG_R0,Q);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001)
 names={'highest':'prvGetDisinheritPriorityAfterTimeout','increment':'pvTaskIncrementMutexHeldCount'};old={'highest':0x441ec4,'increment':0x455ae0};pc=sym[names[kind]] if native else old[kind]
 for i in range(1000):
  u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
  if pc==0x2007f000:break
 else:raise AssertionError('step budget')
 result=u.reg_read(UC_ARM_REG_R0)
 if kind=='highest':assert result==((56-value)&0xffffffff if count else 0)
 else:
  assert result==(0 if current_null else CUR)
  assert word(CUR+100)==(held if current_null else (held+1)&0xffffffff)
 if native:assert observed
 return {'result':result,'held':word(CUR+100),'state_sha256':hashlib.sha256(bytes(u.mem_read(Q,0x4000))).hexdigest()}
rows=[]
for count,value in itertools.product([0,1,3],[0,1,12,47,55,56,57,0x80000000,0xffffffff]):
 c=dict(kind='highest',count=count,value=value);o=helper(False,**c);n=helper(True,**c);assert o==n;rows.append(dict(inputs=c,**o))
for held,current_null in itertools.product([0,1,2,0xfffffffe,0xffffffff],[False,True]):
 c=dict(kind='increment',held=held,current_null=current_null);o=helper(False,**c);n=helper(True,**c);assert o==n;rows.append(dict(inputs=c,**o))
(D/'helper-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Highest-waiter expression direct evaluation including malformed head values; not a real timed-out task trace.','Held-count increment reuses previously attributed public source, including uint32 wrap; no valid live overflowing mutex claim.']},indent=2)+'\n');print('PASS',len(rows),'highest-waiter/held-count helper comparisons')
