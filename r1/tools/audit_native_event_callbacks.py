#!/usr/bin/env python3
"""Authenticate callback bodies, symbol/text relocations and remaining service/ABI gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-event-callbacks';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());c=json.loads((out/'callback-contracts.json').read_text());providers=json.loads((out/'provider-map.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-event-table-prefixes';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-event-table-prefixes-runtime.o')==b['parent_object_sha256']
 assert sha(out/'native-event-callbacks-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-event-callbacks-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==56
 names={x['symbol'] for x in c['callbacks']};assert len(names)==37 and set(b['closed_parent_imports'])==names and len(providers)==50 and len(b['newly_exposed_imports'])==41 and set(b['newly_exposed_imports'])=={n for n in providers.values() if n.startswith('r1_event_service_')}
 assert sha(out/'event-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'event-source.o')[0]==b['graph_undefined_symbols'] and len(b['graph_undefined_symbols'])==49
 assert sha(out/'callback-contracts.json')==b['callback_contracts_sha256'] and sha(out/'provider-map.json')==b['provider_map_sha256'] and sha(out/'text-spans.json')==b['text_spans_sha256'] and b['callback_bodies_compiled']==37
 assert c['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and c['disassembly_sha256']==sha(out/'native-callback-disassembly.txt') and sum(x['reachable_bytes'] for x in c['callbacks'])==1766
 source=(ROOT/b['units'][0]['source']).read_text()
 for row in c['callbacks']:
  assert not row['ghidra_body_used_for_this_recovery'] and 'void '+row['symbol']+'(uint32_t payload' in source
  assert row['reachable_bytes']==sum(x['size'] for x in row['instructions']) and all('EC_'+x['address'][2:]+':' in source for x in row['instructions'])
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_event_callbacks.py')==r['driver_sha256'] and r['comparisons']==53280 and r['counts']==dict(direct=53280,composed=0,faults=792) and set(r['by_body'])=={x['address'] for x in c['callbacks']} and set(r['by_body'].values())=={1440} and sum(r['observation_counts'].values())==54750 and r['trace_sha256']=='da957f07ccedeaeb09bf91ed745d7a37b5e848c0e7306249955258fd2fded52b'
 sections=allocated_sections(out/'native_event_callbacks.o');spans=json.loads((out/'text-spans.json').read_text());assert len(spans)==32 and sum(x['size'] for x in spans if 'section'in x)==815
 for x in spans:
  a=int(x['address'],16);data=binary[a-0x27000:a-0x27000+x['size']];assert data==x['text'].encode()+b'\0'
  if 'section' in x:assert sections[x['section']][2]==x['size'] and sections[x['section']][4]==hashlib.sha256(data).hexdigest()
  else:assert x['address']=='0x42724' and x['alias_of']=='0x42710' and x['alias_offset']==20 and '.set r1_event_text_42724,r1_event_text_42710+20' in source
 assert sha(out/'dispatch-raw-abi-probe.json')==r['composed_dispatch_raw_abi_probe_sha256'];probe=json.loads((out/'dispatch-raw-abi-probe.json').read_text());assert not probe['resolved'] and probe['case']['event_id']==2 and probe['case']['row']['address']=='0x42856'
 a,z=probe['results'];assert a[1][0][0]==z[1][0][0]=='0x8b0fc' and a[1][0][1][:2]==z[1][0][1][:2] and a[1][0][1][2:]==[0x42857,0x98765432] and z[1][0][1][2:]==[0x100080b,0]
 history=json.loads((out/'correction-history.json').read_text())
 for p,h in history['preserved_files'].items():assert sha(out/p)==h,p
 assert history['c_callback_signature_matches_table'] and history['c_type_correction_allocated_sections_identical'] and allocated_sections(out/'native_event_callbacks.o')==allocated_sections(out/'pre-callback-c-type-correction/native_event_callbacks.o')
 frontier=json.loads((out/'service-frontier.json').read_text());assert frontier['provider_map_sha256']==sha(out/'provider-map.json') and frontier['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and len(frontier['services'])==50 and sum(x['new_unresolved_source_body'] for x in frontier['services'])==41 and all(not x['exact_upstream_body_match_proven'] for x in frontier['services'])
 for flag in ['all_37_callback_bodies_execute','services_logging_and_free_are_fixtures']:assert r[flag]
 for flag in ['source_dispatch_tables_and_callbacks_composed','full_private_frame_history_verified','full_raw_abi_verified','full_table_extents_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('Event callbacks:37 bodies/1766 reachable code+815 unique text bytes;53280 scoped checks;56 main imports;dispatcher raw ABI gate open')
if __name__=='__main__':audit()
