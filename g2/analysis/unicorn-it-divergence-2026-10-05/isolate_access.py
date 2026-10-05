#!/usr/bin/env python3
"""Diagnostic-only hook matrix around unchanged linked tick machine code."""
import hashlib,importlib.util,inspect,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('tick_verify',ROOT/'g2/components/foundation/freertos_tick/simulator/verify.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=inspect.getsource(m.run)
old="cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem);"
new="\n if c['hook_mode'] in ['code','both']:cpu.hook_add(u.UC_HOOK_CODE,code)\n if c['hook_mode'] in ['mem','both','read','write']:cpu.hook_add({'read':u.UC_HOOK_MEM_READ,'write':u.UC_HOOK_MEM_WRITE}.get(c['hook_mode'],u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE),mem)\n "
assert old in source;source=source.replace(old,new)
namespace=dict(vars(m));exec(compile(source,str(__file__), 'exec'),namespace);run=namespace['run']
final=json.loads((ROOT/'g2/build/foundation/rtos-tick-wsf-simulator/comparison-verified.json').read_text())
case=next(x['inputs'] for x in final['cases'] if x['inputs']['priority']==3 and x['inputs']['waiter_count']==2 and x['inputs']['wake_times']==[10,10,50] and x['inputs']['event_linked']==[False,False] and not x['inputs']['ready_existing'])
records=[]
reference=None
for profile in ['o2','o2-noalias','o0']:
 path=ROOT/('g2/build/foundation/rtos-tick-wsf-simulator/rtos_tick_wsf.elf' if profile=='o0' else 'g2/build/foundation/rtos-tick-wsf-diagnostic-'+profile+'/rtos_tick_wsf.elf')
 elf,segs,syms=m.parser.elf_info(path)
 for mode in ['none','code','read','write','mem','both']:
  try:
   result=run(segs,{k:syms[n]&~1 for k,n in m.NAMES.items()},{syms[n]&~1:v for n,v in m.SOURCE_BOUNDARIES.items()},syms['opencfw_radio_gpio_callback'],dict(case,hook_mode=mode,yield_entry=syms['opencfw_resume_yield_request']&~1,critical_exit_entry=syms['opencfw_daemon_critical_exit']&~1))
   if reference is None:reference=result['kernel']
   records.append(dict(kernel_equals_first_o2_nohooks=result['kernel']==reference,profile=profile,mode=mode,completed=True,returns=result['returns'],kernel=result['kernel'],elf_sha256=hashlib.sha256(elf).hexdigest()))
  except Exception as e:records.append(dict(profile=profile,mode=mode,completed=False,error=str(e),elf_sha256=hashlib.sha256(elf).hexdigest()))
  print(profile,mode,records[-1]['completed'],records[-1].get('returns'))
out=ROOT/'g2/build/foundation/unicorn-it-divergence/hook-access-matrix.json'
with out.open('x') as f:json.dump(dict(input=case,diagnostic_only=True,records=records),f,indent=2);f.write('\n')
