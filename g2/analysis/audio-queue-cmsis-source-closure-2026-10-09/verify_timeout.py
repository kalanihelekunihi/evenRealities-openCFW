from pathlib import Path
import json,itertools,hashlib
D=Path(__file__).resolve().parent
exec((D/'verify.py').read_text().split('for capacity,size in itertools.product')[0])
rows=[]
def test(native,kind,start_tick=100,now=100,saved_overflow=0,overflow=0,wait=5,nesting=0,mask=0):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M4)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw)
 for a,b in segments:u.mem_write(a,b)
 def w(a,*v):u.mem_write(a,struct.pack('<'+'I'*len(v),*v))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 state=0x20006000;remaining=0x20006200;w(state,saved_overflow,start_tick);w(remaining,wait);w(0x20074a34,now);w(0x20074a48,overflow);w(0x2000309c,nesting);u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_BASEPRI,48 if nesting else 16);u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);u.reg_write(UC_ARM_REG_R0,state);u.reg_write(UC_ARM_REG_R1,remaining)
 seen=[]
 def hook(u,a,n,d):
  assert a not in [0x441800,0x4420f6,0x455574,0x455586],'unexpected assert'
  if native:assert 0x100000<=a<0x110000,('source timeout escaped',hex(a));seen.append(a)
 u.hook_add(UC_HOOK_CODE,hook);pc=(sym['stock_timeout_capture'] if kind=='capture' else sym['stock_timeout_check']) if native else (0x455556 if kind=='capture' else 0x455566)
 for i in range(10000):
  u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
  if pc==0x2007f000:break
 else:raise AssertionError('step limit')
 if native:assert seen
 result=None if kind=='capture' else u.reg_read(UC_ARM_REG_R0)
 if kind=='capture':assert [word(state),word(state+4)]==[overflow,now] and word(remaining)==wait
 else:
  elapsed=(now-start_tick)&0xffffffff;expired=wait!=0xffffffff and ((overflow!=saved_overflow and now>=start_tick) or elapsed>=wait)
  assert result==int(expired) and word(remaining)==(0 if expired else wait if wait==0xffffffff else wait-elapsed)
 return {'return_value':result,'timeout_state':[word(state),word(state+4)],'wait_remaining':word(remaining),'nesting':word(0x2000309c),'basepri':u.reg_read(UC_ARM_REG_BASEPRI),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'sp_restored':u.reg_read(UC_ARM_REG_SP)==0x2007e000}
for now,overflow,mask in itertools.product([0,100,0xfffffffe,0xffffffff],[0,1,0xffffffff],[0,1]):
 c=dict(kind='capture',now=now,overflow=overflow,mask=mask);o=test(False,**c);n=test(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for start_tick,now,overflow,wait,nesting in itertools.product([0,100,0xfffffff0,0xffffffff],[0,99,100,101,0xffffffff],[0,1,0xffffffff],[0,1,5,0xffffffff],[0,2]):
 c=dict(kind='check',start_tick=start_tick,now=now,overflow=overflow,wait=wait,nesting=nesting);o=test(False,**c);n=test(True,**c);assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
(D/'timeout-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Valid state/wait pointers; explicit stock no-task-abort-delay body.','Synthetic stable tick/overflow words, not physical ticks or elapsed wall time.','MAX wait bypasses expiry/state mutation even across overflow; no resumed blocked task.']},indent=2)+'\n');print('PASS',len(rows),'timeout-provider comparisons')
