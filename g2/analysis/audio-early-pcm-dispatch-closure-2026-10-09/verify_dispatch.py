from pathlib import Path
import itertools,json,hashlib
D=Path(__file__).resolve().parent
exec((D/'verify.py').read_text().split('for major,version,date,old in itertools.product')[0])
entries={'buck':0x47fe6c,'before':0x480358,'after':0x48036e,'suspend':0x480384,'lp_init':0x4803ac,'ton':0x4803c2,'early_on':0x59fbac,'early_off':0x59fca2}
names={'buck':'pcm_buck_control','before':'pcm_before_enable_dispatch','after':'pcm_after_enable_dispatch','suspend':'pcm_tempco_suspend_dispatch','lp_init':'pcm_lp_switch_initialize_dispatch','ton':'pcm_ton_dispatch','early_on':'pcm_early_on','early_off':'pcm_early_off'}
profiles={'early':{'before':(0x59fd82,'pcm_early_before_enable'),'after':(0x59fda8,'pcm_early_after_enable')},'middle':{'before':(0x5a081c,'pcm_middle_before_enable'),'after':(0x5a0842,'pcm_middle_after_enable')},'ton':{'ton':(0x59fe5a,'pcm_ton_config_update')},'lp':{'lp_init':(0x5a085e,'pcm_lp_switch_initialize')}}
slots={'before':0x20073284,'after':0x20073288,'suspend':0x2007328c,'lp_init':0x20073290,'ton':0x20073294};rows=[]
def test(native,kind,profile='null',arguments=(),old_register=0xa5a5a5a5,cache_enabled=1,core_cache=1023,mask=0,buck_enabled=1,gate=3,memory_trim=63,state=1):
 u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
 for a,n in [(0x438000,(len(raw)+4095)&~4095),(0x20000000,0x80000),(0x100000,0x10000),(0,0x1000),(0x40020000,0x2000),(0xe000e000,0x2000)]:u.mem_map(a,n)
 u.mem_write(0x438000,raw);u.mem_write(0x20000000,bytes(startup));u.mem_write(0x40,itcm)
 for a,b in segments:u.mem_write(a,b)
 def w(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def word(a):return struct.unpack('<I',u.mem_read(a,4))[0]
 w(0xe000ed88,0xf00000);w(0x40020060,old_register);w(0x2007427c,core_cache);u.mem_write(0x20074f63,bytes([cache_enabled]));w(0x40020080,0xa5a5a400|(core_cache&1023));w(0x40020088,0xabcdefc0|memory_trim);w(0x400201b0,old_register);w(0x40021000,0);w(0x40021100,buck_enabled);w(0x40021108,gate<<4);w(0x40020044,0x76543200|112);w(0x4002004c,0x76543200|112)
 for a in [0x40020374,0x40020380,0x40020344,0x4002034c,0x40020354,0x40020358,0x400211a0,0x400211a4,0x400211a8,0x400211ac,0x400211b4,0x400211bc]:w(a,old_register)
 u.mem_write(0x2000453a,bytes([14,31,11,11,21,31]));u.mem_write(0x20074f73,b'\xa5');w(0x2007426c,112);w(0x20074270,112);w(0x20074274,2);w(0x20074278,1)
 for a in slots.values():w(a,0)
 expected_child=None
 if profile in profiles and kind in profiles[profile]:
  old,name=profiles[profile][kind];w(slots[kind],sym[name] if native else old|1);expected_child=(sym[name]&~1) if native else old
 if profile=='cut_noop':w(slots['suspend'],0x5a0a6d);expected_child=0x5a0a6c
 if kind=='early_sequence':w(slots['ton'],sym['pcm_ton_config_update'] if native else 0x59fe5b)
 u.reg_write(UC_ARM_REG_PRIMASK,mask);u.reg_write(UC_ARM_REG_FPSCR,0);writes=[];calls=[];boundary=[];observed=[]
 def hook(u,a,n,d):
  if a==0x5a0a6c:boundary.append({'kind':'before_selected_noop_child'});u.emu_stop();return
  if native:assert 0x100000<=a<0x110000,('native execution escaped',hex(a));observed.append(a)
  if a==expected_child:calls.append({'call':'registered_child','args':[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)] if kind=='ton' else []})
  if kind=='early_sequence' and a in [0x59fe5a,sym['pcm_ton_config_update']&~1]:calls.append({'call':'ton_callback','args':[u.reg_read(UC_ARM_REG_R0),u.reg_read(UC_ARM_REG_R1)]})
 def wr(u,ac,a,n,v,d):
  if 0x40020000<=a<0x40022000:writes.append([hex(a),n,v])
 u.hook_add(UC_HOOK_CODE,hook);u.hook_add(UC_HOOK_MEM_WRITE,wr)
 def invoke(at,args):
  for r,v in zip([UC_ARM_REG_R0,UC_ARM_REG_R1],args):u.reg_write(r,v)
  u.reg_write(UC_ARM_REG_SP,0x2007e000);u.reg_write(UC_ARM_REG_LR,0x2007f001);pc=at|1
  for i in range(50000):
   u.emu_start(pc|1,0x2007f000,count=1);pc=u.reg_read(UC_ARM_REG_PC)
   if pc==0x2007f000 or boundary:return
  raise AssertionError('instruction step limit')
 if kind=='early_sequence':
  for op,arg in [('early_on',[state]),('early_off',[])]:invoke(sym[names[op]] if native else entries[op],arg)
 else:invoke(sym[names[kind]] if native else entries[kind],arguments)
 if kind=='buck':
  bit=arguments[0]&1;expected=(old_register&~0x10021)|(bit*0x10021);assert word(0x40020060)==expected
  assert [x[0] for x in writes]==['0x40020060']*3
 if kind=='ton' and calls:assert calls[0]['args']==[x&255 for x in arguments]
 regions=[(0x2007426c,92),(0x20074f60,32),(0x2000453a,6),(0x40020000,0x2000)]
 return {'return_value':None if kind=='buck' or boundary else u.reg_read(UC_ARM_REG_R0),'calls':calls,'boundary':boundary,'writes':writes,'state_digest':hashlib.sha256(b''.join(bytes(u.mem_read(a,n)) for a,n in regions)).hexdigest(),'primask':u.reg_read(UC_ARM_REG_PRIMASK),'fpscr':u.reg_read(UC_ARM_REG_FPSCR),'source_guard_pass':bool(observed) if native else None}
def compare(c):
 o=test(False,**c);n=test(True,**c);assert n.pop('source_guard_pass');o.pop('source_guard_pass');assert o==n,(c,o,n);rows.append(dict(inputs=c,**o))
for enable,old_register,mask in itertools.product([0,1,2,3,255,256,257,0xffffffff],[0,0xffffffff,0xa5a5a5a5,0x10000],[0,1]):compare(dict(kind='buck',arguments=[enable],old_register=old_register,mask=mask))
for profile,cache_enabled,core_cache,mask in itertools.product(['null','early','middle'],[0,1],[0,5,6,7,8,1023],[0,1]):compare(dict(kind='before',profile=profile,cache_enabled=cache_enabled,core_cache=core_cache,mask=mask))
for profile,memory_trim,mask in itertools.product(['null','early','middle'],[0,1,63],[0,1]):compare(dict(kind='after',profile=profile,memory_trim=memory_trim,mask=mask))
for profile,old_register,mask in itertools.product(['null','lp'],[0,0xffffffff,0xa5a5a5a5],[0,1]):compare(dict(kind='lp_init',profile=profile,old_register=old_register,mask=mask))
for profile,gpu_on,gpu_mode,buck_enabled,mask in itertools.product(['null','ton'],[0,1,2,255,256,257],[0,1,2,255,256],[0,1],[0,1]):compare(dict(kind='ton',profile=profile,arguments=[gpu_on,gpu_mode],buck_enabled=buck_enabled,mask=mask))
for profile,mask in itertools.product(['null','cut_noop'],[0,1]):compare(dict(kind='suspend',profile=profile,mask=mask))
for state,gate,cache_enabled,core_cache,memory_trim in itertools.product([1,2],[0,3],[0,1],[0,1023],[58,63]):compare(dict(kind='early_sequence',state=state,gate=gate,cache_enabled=cache_enabled,core_cache=core_cache,memory_trim=memory_trim))
(D/'dispatch-results.json').write_text(json.dumps({'status':'PASS','cases':len(rows),'elf_sha256':receipt['elf_sha256'],'comparisons':rows,'limits':['Six new stock register/dispatch providers; real native before/after/TON/LP-init children compiled unchanged from sealed sources.','Temperature-suspend non-NULL case stops before a selected real noop child, not claimed stock registration or full suspend implementation.','Source guard applies to every reached native instruction; no original helper fallback except before-entry cut.','Passive MMIO and synthetic registry/cache/silicon fields do not establish physical rail settling or runtime callback registration.']},indent=2)+'\n');print('PASS',len(rows),'buck/dispatch/source-only GPU comparisons')
