#!/usr/bin/env python3
"""Authenticate health command bodies, source helpers and exposed dispatch leaf gates."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-commands';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');obj=OUT/'native_health_commands.o';raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
 assert r['comparisons']==46080 and len(r['counts'])==16 and all(n==(2048 if name.startswith('r1_protocol_send_flag_set_') else 3072) for name,n in r['counts'].items())
 assert r['response_calls_per_side']==11520 and r['event_calls_per_side']==8448 and r['trace_sha256']=='99c05f3c6482e750f97f40817c0e03e210e6133b326af3cefdc452f612b670b1'
 for flag in ['all_256_flag_bytes','actual_source_flag_helpers_execute','only_lower_response_event_setting_providers_are_fixtures','event_seed_word_retained_not_zeroed','sequence_reloaded_after_response_and_no_flag_recheck','report_length12_address0_read_is_explicit_fixture','unaligned_packets_and_header_truncations_checked','raw_r0_callee_sp_and_observed_nonstack_ram_checked','private_event_header_pointers_not_compared','candidate_native_execution_forbidden']:assert r[flag]
 assert not r['whole_dispatch_graph_executed'] and not r['physical_delivery_verified'] and not r['instruction_identity'] and not r['whole_image_complete']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_health_commands.py') and r['report_sha256']==sha(rp) and r['object_sha256']==report['units'][0]['object_sha256']==sha(obj) and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_health_commands_verification.ld') and r['application_sha256']==hashlib.sha256(raw).hexdigest()
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 for p in OUT.glob('ghidra-*.json'):
  g=read(p);a=int(g['address'],16);assert bytes(g['data'])==raw[a-0x27000:a-0x27000+g['length']]
 for p in OUT.glob('rea-*.json'):
  q=read(p);q=q.get('structuredContent') or json.loads(next(x['text'] for x in q['content'] if x['type']=='text'));a=int(p.stem.split('-')[1],16)
  if a in [0x8280c,0x82844,0x8287c]:assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==56
  else:assert 'No procedure exists' in str(q)
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['ownership_rows'])==16 and all(row in rows for row in e['ownership_rows']) and sum(int(x['size']) for x in e['ownership_rows'])==844
 assert e['native_event_seed_is_incoming_r3'] and e['daily_sequence_reloaded_after_response'] and not e['whole_image_identity'] and not e['full_cross_translation_unit_callback_types_verified']
 history=OUT/'initial-pointer-typed-candidate';m=read(history/'manifest.json')
 for p,h in m['files'].items():assert sha(history/p)==h,p
 bp=BASE/'native-health-commands-runtime/report.json';b=read(bp);assert b['linked_sha256']==sha(bp.parent/'native-health-commands-runtime.o') and len(b['undefined_symbols'])==78 and len(b['closed_parent_imports'])==3 and len(b['newly_exposed_imports'])==25 and b['all_three_dispatchers_source_linked'] and not b['whole_dispatch_graph_executed'] and not b['full_cross_translation_unit_callback_types_verified'] and not b['whole_image_complete']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-health-commands-runtime.o')[0]==b['undefined_symbols']

 g=read(bp.parent/'graph-verification.json');assert g['comparisons']==43008 and len(g['counts'])==14 and all(n==3072 for n in g['counts'].values()) and g['response_calls_per_side']==5376 and g['event_calls_per_side']==9216 and g['trace_sha256']=='fc70cf30f04ff998078f24f6e433ff28842e9410395b1722c9ab9b1d39979b3b'
 assert g['actual_source_dispatch_search_all14_handlers'] and g['actual_source_flag_helpers_execute'] and g['only_lower_response_event_setting_providers_are_fixtures'] and g['bounded_health_dispatch_graph_executed'] and not g['whole_dispatch_graph_executed'] and not g['whole_image_complete'] and not g['instruction_identity']
 assert g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_health_dispatch_graph.py') and g['report_sha256']==sha(bp) and g['object_sha256']==b['graph_object_sha256']==sha(bp.parent/'health-dispatch-graph-source.o') and g['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_health_dispatch_graph_verification.ld') and g['application_sha256']==r['application_sha256']
 assert b['selected_dispatch_object_sha256']==sha(bp.parent/'health-dispatch-source.o') and b['graph_undefined_symbols']==['r1_event_publish','r1_protocol_send_response','r1_service_health_report_set'] and undefined_symbols(bp.parent/'health-dispatch-graph-source.o')[0]==b['graph_undefined_symbols']
 print('Health commands authenticated:46080 cases +43008 dispatcher workflows;16 rows844 native bytes;dispatch source-linked with78 imports;private ABI/legacy declarations/provider/image gates open')
if __name__=='__main__':audit()
