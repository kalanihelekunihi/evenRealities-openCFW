from pathlib import Path
import itertools,json,hashlib,struct
D=Path(__file__).resolve().parent
exec(compile((D/'machine.py').read_text(),str(D/'machine.py'),'exec'))
entries={'early_before_enable':0x59fd82,'early_after_enable':0x59fda8,'middle_before_enable':0x5a081c,'middle_after_enable':0x5a0842,'lp_switch_initialize':0x5a085e,'lp_switch_enable':0x5a08b6,'lp_switch_disable':0x5a08ca,'hardware_temperature':0x5a001c,'postpone':0x5a07e6,'pending_handle':0x5a07f0,'ton_initialize':0x59fdc2,'ton_config_update':0x59fe5a,'early_control':0x59fd36,'middle_control':0x5a0786,'early_switch':0x59fb70,'early_on':0x59fbac,'early_off':0x59fca2,'temperature_publish':0x5a00c8,'temperature':0x5a00fc,'sleep':0x5a0204,'middle_on':0x5a0328,'middle_off':0x5a05e0}
providers={0x4807a0:1,0x4803c2:2,0x47fe6c:1,0x473940:0,0x48d620:0,0x5a001c:1,0x59fb70:1,0x5a00c8:1}
void={'hardware_temperature','early_switch','temperature_publish','sleep'}
def test(native,kind,args=None,gate=3,flag63=1,flag6f=1,flag6e=0,flag67=0,flag71=0,oldrange=0,core=0,mem=0,trim=0,cache=0,bits=0,mask=0,words=None,flags=None,steps=None,ton_callback=0):
 u=machine();w(u,0x20073294,((sym['pcm_ton_config_update'] if native else 0x59fe5b) if ton_callback else 0));w(u,0x40021108,gate<<4);w(u,0x40020080,0xa5a5a400|core);w(u,0x40020088,0xabcdefc0|mem)
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
  if native:a={sym['pcm_hardware_temperature']&~1:0x5a001c,sym['pcm_early_switch']&~1:0x59fb70,sym['pcm_temperature_publish']&~1:0x5a00c8}.get(a,a)
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
 return dict(ton_cache=bytes(u.mem_read(0x2000453a,6)).hex(),status=None if kind in void else u.reg_read(UC_ARM_REG_R0),calls=calls,writes=writes,cache=bytes(u.mem_read(0x2007426c,92)).hex(),globals=bytes(u.mem_read(0x20074f60,32)).hex(),metadata=bytes(u.mem_read(0x20006000,12)).hex(),primask=u.reg_read(UC_ARM_REG_PRIMASK))
cases=[]
for rng,gate,cached,gpu,variant,base in itertools.product([0,1,2,3,255,256,257],[0,3],[0,1],[0,0x40000],[0,1],[0,9,10,11,112,127,0xffffffff]):
 cases.append(('hardware_temperature',dict(args=[rng],gate=gate,flag63=cached,flag6f=variant,cache=base,words=[[0x40021004,gpu]])))
for block,pending,rng,gate,cached,mask in itertools.product([0,1],[0,1],[0,1,2,255],[0,3],[0,1],[0,1]):
 cases.append(('pending_handle',dict(args=[],gate=gate,flag63=cached,oldrange=rng,mask=mask,cache=42,flags=[[0x20074f71,block],[0x20074f72,pending]])))
for oldpending in [0,1,255]:cases.append(('postpone',dict(args=[],flags=[[0x20074f71,0],[0x20074f72,oldpending]],steps=[('postpone',[]),('postpone',[])])))
for gate,cached,gpu,mask in itertools.product([0,3],[0,1],[0,0x40000],[0,1]):
 cases.append(('pending_handle',dict(gate=gate,flag63=cached,cache=42,mask=mask,words=[[0x40021004,gpu]],steps=[('postpone',[]),('temperature_publish',[0]),('postpone',[]),('temperature_publish',[2]),('pending_handle',[]),('pending_handle',[])])))
for major,revision,pattern in itertools.product([0x20,0x21,0x22,0x23,0xff],[0,1,0xffffffff],[0,0xffffffff,0x12345678]):
 cases.append(('ton_initialize',dict(args=[],words=[[0x4002000c,major],[0x200001e8,revision]]+[[a,pattern] for a in [0x40020344,0x4002034c,0x40020354,0x40020358]])))
for on,mode,enabled,cache in itertools.product([0,1,2,255,256,257],[0,1,255,256,257],[0,1],[0,31,255]):
 flags=[[0x2000453a,cache],[0x2000453b,cache^31],[0x2000453c,cache^17],[0x2000453d,cache^5],[0x2000453e,cache^11],[0x2000453f,cache^23]]
 cases.append(('ton_config_update',dict(args=[on,mode],words=[[0x40021100,0x12345678|enabled]],flags=flags)))
for enabled,major,rev in itertools.product([0,1],[0x20,0x21,0x22],[0,1]):
 cases.append(('ton_config_update',dict(args=[1,1],words=[[0x40021100,enabled],[0x4002000c,major],[0x200001e8,rev]],steps=[('ton_initialize',[]),('ton_config_update',[1,0]),('ton_config_update',[1,1]),('ton_config_update',[0,0])])) )
for kind,control,owned in itertools.product(['lp_switch_initialize','lp_switch_enable','lp_switch_disable'],[0,3,0xffffffff,0x12345678],[0,1,255]):
 cases.append((kind,dict(args=[],words=[[0x400211a0,control]],flags=[[0x20074f73,owned]])))
for owned,control in itertools.product([0,1],[0,3,0xffffffff]):
 cases.append(('lp_switch_disable',dict(args=[],words=[[0x400211a0,control]],flags=[[0x20074f73,owned]],steps=[('lp_switch_initialize',[]),('lp_switch_enable',[]),('lp_switch_enable',[]),('lp_switch_disable',[]),('lp_switch_disable',[])])))
for kind,cached,valid in itertools.product(['early_before_enable','early_after_enable','middle_before_enable','middle_after_enable'],[0,6,7,8,1023,1024,0xffffffff],[0,1]):
 cases.append((kind,dict(args=[],cache=cached,flag63=valid)))
rows=[]
for kind,case in cases:
 o=test(False,kind,**case);n=test(True,kind,**case);assert o==n,(kind,case,o,n);rows.append(dict(function=kind,inputs=case,**o))
(D/'pending-results.json').write_text(json.dumps(dict(status='PASS',cases=len(rows),counts={kind:sum(x['function']==kind for x in rows) for kind in ['hardware_temperature','postpone','pending_handle','ton_initialize','ton_config_update','lp_switch_initialize','lp_switch_enable','lp_switch_disable','early_before_enable','early_after_enable','middle_before_enable','middle_after_enable']},elf_sha256=hashlib.sha256(elf.read_bytes()).hexdigest(),comparisons=rows,limits=['Native temperature/pending/TON bodies; common delay, IRQ-save and buck-register provider execute original instructions.','Synthetic cached trims, variant/peripheral flags and passive MMIO; not measured physical rail effects.','Direct function entry with PRIMASK checks, not live task/NVIC exception proof.']),separators=(',',':'))+'\n');print('PASS',len(rows),'early PCM pending/TON comparisons')
