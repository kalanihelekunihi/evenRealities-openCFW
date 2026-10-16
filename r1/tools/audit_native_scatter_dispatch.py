#!/usr/bin/env python3
"""Audit source scatter dispatch up to an explicitly unexecuted application boundary."""
import contextlib,hashlib,io,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-scatter-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 from audit_native_scatter_data import audit as history
 with contextlib.redirect_stdout(io.StringIO()):history()
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();bp=BASE/'native-scatter-runtime/report.json';bundle=read(bp)
 assert r['trace_sha256']=='1c4bf6b5e24c91f92ae9e45f6f01bca9127416ce6f5deefdab60059a57f709e2'
 assert r['comparisons']==14 and r['provider_counts']=={side:{'decompress':14,'zero':14} for side in ['native','compiled']}
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_scatter_dispatch.py') and r['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a' and r['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
 assert r['report_sha256']==sha(rp) and r['object_sha256']==sha(OUT/'native_scatter_dispatch.o')==report['units'][0]['object_sha256'] and r['runtime_report_sha256']==sha(bp) and r['runtime_object_sha256']==sha(bp.parent/'native-scatter-runtime.o')==bundle['linked_sha256']
 assert r['layout_sha256']==sha(ROOT/r['layout']) and not r['instruction_identity'] and r['unresolved_source_providers']==bundle['undefined_symbols']==['r1_native_application_entry'] and not r['runtime_no_unresolved'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for flag in ['full_ram_and_provider_arguments_and_nonstack_write_order_checked','executed_store_observer_with_full_ram_reconciliation','unicorn_memory_write_hooks_disabled','candidate_native_code_execution_forbidden','source_dispatch_providers_and_callback_configuration','source_runtime_handoff_body','application_body_terminal_boundary_fixture']:assert r[flag]
 assert r['runtime_entry_calls_per_case']==1 and not r['application_body_executed'] and not r['initialized_data_source_ownership']
 assert r['handoff_sp_equal'] and not r['handoff_raw_registers_equal']
 assert len(r['handoffs'])==14
 for native,source in r['handoffs']:assert native['pc']==0x75f64 and source['pc']==0x20000200
 assert r['handoff_sp_equal']==all(a['sp']==b['sp'] for a,b in r['handoffs']) and r['handoff_raw_registers_equal']==all(a['registers']==b['registers'] for a,b in r['handoffs'])
 for data in [report,bundle]:
  for p,h in data['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 assert bundle['provider_reports']=={p:sha(BASE/p) for p in ['native-scatter-dispatch/report.json','native-scatter-data/report.json']}
 assert 'PROVIDE(r1_native_application_entry = 0x20000201)' in (ROOT/r['layout']).read_text()
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x283a0,36),(0x27208,8),(0x75f64,146)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a in [0x27208,0x75f64]:
  evidence=read(OUT/f'rea-{a:x}.json');evidence=evidence.get('structuredContent') or json.loads(next(x['text'] for x in evidence['content'] if x['type']=='text'));assert evidence['error']['code']=='invalid_request' and 'No procedure exists' in str(evidence)
 assert e['native_dispatch_bytes']==28 and e['native_dispatch_literals_bytes']==8 and e['native_handoff_body_bytes']==4 and e['native_handoff_literal_bytes']==4 and e['actual_dispatch_does_not_include_scanf'] and not e['locked_ownership_changed']
 assert e['prior_provider_evidence_sha256']==sha(BASE/'native-scatter-data/evidence.json') and e['application_boundary_fixture'] and not e['application_body_executed'] and not e['compressed_initialization_source_ownership']
 abi=read(OUT/'handoff-abi-gate.json');assert e['handoff_abi_gate_sha256']==sha(OUT/'handoff-abi-gate.json') and abi['status']=='open-raw-handoff-abi-difference' and abi['verification_sha256']==sha(OUT/'verification.json') and abi['handoff_sp_equal'] and not abi['raw_registers_equal'] and not abi['external_blocker']
 assert e['application_next_contract_sha256']==sha(OUT/'application-entry-next-contract.json')
 print('Source scatter dispatch and runtime handoff authenticated to unexecuted application boundary; application, raw ABI and image gates remain open')
if __name__=='__main__':audit()
