#!/usr/bin/env python3
"""Reproduce excluded optimized-profile divergence; never contributes coverage."""
import hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('tick_verify',ROOT/'g2/components/foundation/freertos_tick/simulator/verify.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
build=ROOT/'g2/build/foundation/rtos-tick-wsf-simulator'
final=json.loads((build/'comparison-final.json').read_text())
case=next(x['inputs'] for x in final['cases'] if x['inputs']['priority']==3 and x['inputs']['waiter_count']==2 and x['inputs']['wake_times']==[10,10,50] and x['inputs']['event_linked']==[False,False] and not x['inputs']['ready_existing'])
elf_path=ROOT/'g2/build/foundation/rtos-tick-wsf-diagnostic-o2/rtos_tick_wsf.elf'
elf,segs,syms=m.parser.elf_info(elf_path)
blob=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
stock=[dict(address=m.BASE,data=blob[32:],memory_size=len(blob)-32,flags=5)]
original=m.run(stock,m.ORIGINAL,m.BOUNDARIES,0x4b4a98,dict(case,yield_entry=0x4420bc,critical_exit_entry=0x4420e8))
error=None
try:
 source=m.run(segs,{k:syms[n]&~1 for k,n in m.NAMES.items()},{syms[n]&~1:v for n,v in m.SOURCE_BOUNDARIES.items()},syms['opencfw_radio_gpio_callback'],dict(case,yield_entry=syms['opencfw_resume_yield_request']&~1,critical_exit_entry=syms['opencfw_daemon_critical_exit']&~1))
 same={k:v for k,v in original.items() if k!='trace'}=={k:v for k,v in source.items() if k!='trace'}
except Exception as e:error=str(e);same=False
report=dict(status='DIAGNOSTIC_DIVERGENCE' if not same else 'DIAGNOSTIC_MATCH',counted_as_passing_coverage=False,inputs=case,source_error=error,stock_completed=True,optimized_elf=str(elf_path.relative_to(ROOT)),optimized_elf_sha256=hashlib.sha256(elf).hexdigest(),firmware_sha256=hashlib.sha256(blob).hexdigest(),verifier_sha256=hashlib.sha256((ROOT/'g2/components/foundation/freertos_tick/simulator/verify.py').read_bytes()).hexdigest(),replica_note='O2 diagnostic ELF reconstructed from unchanged function texts/effective original optimization flags. It is not claimed to be a retained copy with a previously recorded original ELF hash.',execution_policy=final['execution_policy'])
out=build/'diagnostics/optimized-replica.json'
with out.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
print(report['status'],'excluded from passing coverage')
