from pathlib import Path
p=Path(__file__).resolve().parent.parent/'case-wave056-timer-trampoline-binding/check.py';ns={'__file__':str(p)};exec(p.read_text().split('rows=[]')[0],ns);globals().update({k:v for k,v in ns.items() if k!='__file__'});OUT=Path(__file__).resolve().parent
rows=[]
for cb in callbacks:
 for mode in [0,1]:
  for arg in [0,0xffffffff]:
   for variant in ['dynamic','static44','invalid43','invalid_no_storage']:
    results=[]
    for source in [False,True]:
     u=Uc(UC_ARCH_ARM,UC_MODE_THUMB|UC_MODE_MCLASS);u.mem_map(0x8000000,0x20000);u.mem_map(0x20000000,0x10000);u.mem_map(0xe000e000,0x2000)
     if source:
      for a,d in segs:u.mem_write(a,d)
      entry=syms['case_boot_transport_register'];target=syms[cb[1]]&~1;trampoline=syms['case_boot_transport_entry_8558'];ctors={syms['case_boot_transport_register_dynamic']&~1:'dynamic',syms['case_boot_transport_register_static']&~1:'static'}
     else:u.mem_write(0x8000000,raw);entry=0x800aa49;target=0x8000000+cb[0];trampoline=0x8008559;ctors={0x800ccc0:'dynamic',0x800ccf2:'static'}
     descriptor=0 if variant=='dynamic' else 0x20004000
     if descriptor:u.mem_write(descriptor,struct.pack('<IIII',0,0,0x20005000 if variant!='invalid_no_storage' else 0,44 if variant!='invalid43' else 43))
     for reg,v in [(UC_ARM_REG_SP,0x20002c88),(UC_ARM_REG_LR,0x801ff01),(UC_ARM_REG_R0,target|1),(UC_ARM_REG_R1,mode),(UC_ARM_REG_R2,arg),(UC_ARM_REG_R3,descriptor)]:u.reg_write(reg,v)
     state={'constructors':[]};low=[0x20002c88]
     def hook(uc,pc,size,data):
      low[0]=min(low[0],uc.reg_read(UC_ARM_REG_SP))
      if pc in ctors:state['constructors'].append(ctors[pc])
      if pc==0x801ff00:state['result']=uc.reg_read(UC_ARM_REG_R0);uc.emu_stop()
      if pc==target:state['callback_argument']=uc.reg_read(UC_ARM_REG_R0);uc.emu_stop()
     u.hook_add(UC_HOOK_CODE,hook);u.emu_start(entry,0,count=100000);assert 'result' in state
     obj=state['result'];expected=variant in ['dynamic','static44'];assert bool(obj)==expected
     if obj:
      words=struct.unpack('<11I',u.mem_read(obj,44));pair=words[7];pv=struct.unpack('<II',u.mem_read(pair,8));assert pv==(target|1,arg);assert words[8]==trampoline
      assert state['constructors']==(['dynamic'] if variant=='dynamic' else ['static'])
      state['pair_argument']=pv[1];state['mode_byte']=bytes(u.mem_read(obj+40,1))[0]
      # Same live allocation and task object, actual lookup and callback transfer.
      u.reg_write(UC_ARM_REG_R0,obj);u.reg_write(UC_ARM_REG_LR,0x801ff01);u.emu_start(trampoline,0,count=10000);assert state['callback_argument']==arg
     else:assert state['constructors']==[]
     state['bounded_stack_bytes']=0x20002c88-low[0];results.append(state)
    assert {k:v for k,v in results[0].items() if k!='bounded_stack_bytes'}=={k:v for k,v in results[1].items() if k!='bounded_stack_bytes'}
    rows.append(dict(callback_native=hex(0x8000000+cb[0]),source_symbol=cb[1],mode=mode,argument=hex(arg),variant=variant,native=results[0],source=results[1]))
(OUT/'verification.json').write_text(json.dumps(dict(status='PASS_96_REAL_REGISTRATION_TO_CALLBACK_ENTRY_PAIRS',comparisons=rows,limits=['Fresh RAM/heap fixture; real allocation, constructor, list/lock/free and trampoline providers, no provider stubs','Static44 descriptor is synthetic valid API input; shipped six descriptor rows use dynamic branch','Callback bodies stopped at entry; no asynchronous delete/reuse or real timer execution lifetime proven','Observed synchronous stack maximum is not a global IRQ bound']),indent=2)+'\n');print('PASS',len(rows),max(r['source']['bounded_stack_bytes'] for r in rows))
