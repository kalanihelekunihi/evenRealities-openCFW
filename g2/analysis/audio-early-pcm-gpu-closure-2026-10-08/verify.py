from pathlib import Path
import itertools,json,hashlib,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'early_control':0x59fd36,'middle_control':0x5a0786,'early_switch':0x59fb70,'early_on':0x59fbac,'early_off':0x59fca2,'temperature_publish':0x5a00c8,'temperature':0x5a00fc,'sleep':0x5a0204,'middle_on':0x5a0328,'middle_off':0x5a05e0}
providers={0x4807a0:1,0x4803c2:2,0x47fe6c:1,0x473940:0,0x48d620:0,0x5a001c:1,0x59fb70:1,0x5a00c8:1}
void={'early_switch','temperature_publish','sleep'}
def test(native,kind,args=None,gate=3,flag63=1,flag6f=1,flag6e=0,flag67=0,flag71=0,oldrange=0,core=0,mem=0,trim=0,cache=0,bits=0,mask=0,words=None,flags=None,steps=None,ton_callback=0):
 u=machine();w(u,0x20073294,0x59fe5b if ton_callback else 0);w(u,0x40021108,gate<<4);w(u,0x40020080,0xa5a5a400|core);w(u,0x40020088,0xabcdefc0|mem)
 for a in [0x40020044,0x4002004c]:w(u,a,0x76543200|trim)
 for a in [0x40020374,0x40020380,0x40020344,0x4002034c,0x40020354,0x40020358,0x400201b0,0x40021100]:w(u,a,0x87654321)
 for a in range(0x2007426c,0x200742c8,4):w(u,a,cache)
 u.mem_write(0x20074f60,b'\0'*32)
 for a,v in [(0x20074f63,flag63),(0x20074f6f,flag6f),(0x20074f6e,flag6e),(0x20074f67,flag67),(0x20074f71,flag71),(0x20074f74,oldrange),(0x20074f7b,0xa5)]:u.mem_write(a,bytes([v]))
 for a,v in words or []:w(u,a,v)
 for a,v in flags or []:u.mem_write(a,bytes([v]))
 w(u,0x20006000,bits);w(u,0x20006004,0xa5a5a5a5);w(u,0x20006008,0x5a5a5a5a)
 u.reg_write(UC_ARM_REG_PRIMASK,mask);calls=[];writes=[]
 def code(u,a,n,d):
  if native:a={sym['pcm_early_switch']&~1:0x59fb70,sym['pcm_temperature_publish']&~1:0x5a00c8}.get(a,a)
  if a in providers:calls.append([hex(a),[u.reg_read(r) for r in [UC_ARM_REG_R0,UC_ARM_REG_R1][:providers[a]]]])
 def write(u,ac,a,n,v,d):writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_CODE,code)
 for a,b in [(0x40020000,0x40021fff),(0x40008000,0x40008fff),(0x40004000,0x40004fff),(0xe000e100,0xe000e2ff),(0xe000ed14,0xe000ed17),(0xe000ef50,0xe000ef53)]:u.hook_add(UC_HOOK_MEM_WRITE,write,begin=a,end=b)
 if args is None:args=[0x20006000] if kind=='temperature' else [1]
 for step,step_args in (steps or [(kind,args)]):
  u.reg_write(UC_ARM_REG_LR,0x2007f001)
  for reg,value in zip([UC_ARM_REG_R0,UC_ARM_REG_R1,UC_ARM_REG_R2],step_args):u.reg_write(reg,value)
  try:u.emu_start((sym['pcm_'+step] if native else entries[step])|1,0x2007f000,count=1000000)
  except UcError as e:raise AssertionError((native,step,hex(u.reg_read(UC_ARM_REG_PC)),e))
  assert u.reg_read(UC_ARM_REG_PC)==0x2007f000,('limit',native,step,hex(u.reg_read(UC_ARM_REG_PC)))
 return dict(status=None if kind in void else u.reg_read(UC_ARM_REG_R0),calls=calls,writes=writes,cache=bytes(u.mem_read(0x2007426c,92)).hex(),globals=bytes(u.mem_read(0x20074f60,32)).hex(),metadata=bytes(u.mem_read(0x20006000,12)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for kind,state,gate,flag,core,mem,trim in itertools.product(['early_on','early_off','middle_on','middle_off'],[1,2,257],[0,3],[0,1],[0,1011,1012,1023],[0,58,59,63],[0,9,15,112,118,127]):
 cases.append((kind,dict(args=[state],gate=gate,flag63=flag,flag6f=flag,core=core,mem=mem,trim=trim,cache=trim)))
for kind,value in itertools.product(['early_switch','temperature_publish'],[0,1,2,255,256,257]):
 for mask in [0,1]:cases.append((kind,dict(args=[value],mask=mask,flag71=1)))
for bits,flag67,flag71,old,mask in itertools.product([0xc3888001,0xc3888000,0,0x4203ffff,0x42040000,0x420bffff,0x420c0000,0x4247ffff,0x42480000,0x4479ffff,0x447a0000,0x7fc00000,0x7f800000,0xff800000],[0,1],[0,1],[0,1,2],[0,1]):
 cases.append(('temperature',dict(bits=bits,flag67=flag67,flag71=flag71,oldrange=old,mask=mask)))
for temp_range,flag,clk,index,enabled in itertools.product([0,1,2,3],[0,1],[0,5,6,18,19,24,25,255,256,479,480,511],[0,15],[0,1]):
 cases.append(('sleep',dict(oldrange=temp_range,flag67=flag,words=[[0x40008200+32*index,(clk<<8)|enabled],[0x40008010,1<<index]])))
for clk,high,running in itertools.product([0,1,2,3,15],[0,0x40000000,0x80000000],[0,1]):
 cases.append(('sleep',dict(flag67=1,words=[[0x40008800,clk|high]],flags=[[0x20074f7a,running]])))
for kind,action,gate,flag,value in itertools.product(['early_control','middle_control'],[0,1,2,3,256,257],[0,3],[0,1],[0,1,2]):
 cases.append((kind,dict(args=[action,1,0x20006000],gate=gate,flag63=flag,flag6f=flag,flag67=flag,bits=value)))
for kind,trim,cache in itertools.product(['early_on','early_off','middle_on','middle_off'],[0,127],[0xffffffff,0x12345678]):
 cases.append((kind,dict(flag6e=1,trim=trim,cache=cache,args=[2])))
for family,state,trim,flag,memflag in itertools.product(['early','middle'],[1,2],[0,110,127],[0,1],[0,1]):
 cases.append((family+'_on',dict(args=[state],trim=trim,cache=trim,core=1012,mem=63,flag63=flag,flag6f=flag,flag6e=memflag,steps=[(family+'_on',[state]),(family+'_on',[state]),(family+'_off',[])])))
for kind,state,gate,flag,core in itertools.product(['early_on','early_off'],[1,2],[0,3],[0,1],[0,1023]):
 cases.append((kind,dict(args=[state],gate=gate,flag63=flag,core=core,ton_callback=1)))
rows=[]
for kind,case in cases:
 o=test(False,kind,**case);n=test(True,kind,**case);assert o==n,(kind,case,o,n);rows.append(dict(function=kind,inputs=case,**o))
(D/'results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),counts={kind:sum(x['function']==kind for x in rows) for kind in entries},elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Original delay/Ton dispatch/buck-register/STIMER/temperature-apply providers execute without return stubs.','Synthetic trim caches and passive MMIO; no real rail settling or live scheduler/IRQ proof.','Selected M33-compatible instructions; full M55 behavior unverified.']),separators=(',',':'))+'\n');print('PASS',len(rows),'early PCM GPU/temperature comparisons')
