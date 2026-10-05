#!/usr/bin/env python3
"""Diagnostic stock/model comparison; no-memory-hook source is NOT full validation."""
import hashlib,importlib.util,inspect,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('tick_verify',ROOT/'g2/components/foundation/freertos_tick/simulator/verify.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=inspect.getsource(m.run);old='cpu.hook_add(u.UC_HOOK_CODE,code);cpu.hook_add(u.UC_HOOK_MEM_READ|u.UC_HOOK_MEM_WRITE,mem);';assert old in source
ns=dict(vars(m));exec(compile(source.replace(old,'cpu.hook_add(u.UC_HOOK_CODE,code);'),str(__file__),'exec'),ns);no_mem=ns['run']
c=json.loads((ROOT/'g2/build/foundation/unicorn-it-divergence/hook-access-matrix.json').read_text())['input'];c=dict(c,program=[['tick',0,0]],remaining_delayed=0)
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();assert m.sha(blob)=='36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863'
stock=[dict(address=m.BASE,data=blob[32:],memory_size=len(blob)-32,flags=5)]
x=m.run(stock,m.ORIGINAL,m.BOUNDARIES,0x4b4a98,dict(c,yield_entry=0x4420bc,critical_exit_entry=0x4420e8));m.graph_expected(c,x);stock_trace=x.pop('trace');records=[]
for profile in ['o2','o2-noalias','o0']:
 path=ROOT/('g2/build/foundation/rtos-tick-wsf-simulator/rtos_tick_wsf.elf' if profile=='o0' else 'g2/build/foundation/rtos-tick-wsf-diagnostic-'+profile+'/rtos_tick_wsf.elf')
 elf,segs,syms=m.parser.elf_info(path)
 y=no_mem(segs,{k:syms[n]&~1 for k,n in m.NAMES.items()},{syms[n]&~1:v for n,v in m.SOURCE_BOUNDARIES.items()},syms['opencfw_radio_gpio_callback'],dict(c,yield_entry=syms['opencfw_resume_yield_request']&~1,critical_exit_entry=syms['opencfw_daemon_critical_exit']&~1));m.graph_expected(c,y);source_trace=y.pop('trace');assert x==y,(profile,{k:(x[k],y[k]) for k in x if x[k]!=y[k]})
 records.append(dict(profile=profile,elf_sha256=m.sha(elf),stock_final_state_equal=True,independent_graph_model_pass=True,result=y,source_trace=source_trace))
out=ROOT/'g2/build/foundation/unicorn-it-divergence/bounded-stock-comparison.json';out.write_text(json.dumps(dict(input=c,stock_result=x,stock_trace=stock_trace,firmware_sha256=m.sha(blob),records=records,limits='One valid two-expiry input only; source memory-hook invariants absent in this diagnostic. Does not replace full optimized comparison.'),indent=2)+'\n');print('PASS one two-expiry case stock/model/final-state comparison: O2, O2-noalias, O0')
