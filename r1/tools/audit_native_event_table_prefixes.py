#!/usr/bin/env python3
"""Authenticate source-owned bounded event tables and explicit missing callback bodies."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-event-table-prefixes';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());c=json.loads((out/'prefix-contracts.json').read_text());cold=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(cold)==c['cold_data_sha256']=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317';data=cold.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-gxt-call-frames';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-gxt-call-frames-runtime.o')==b['parent_object_sha256']
 assert sha(out/'native-event-table-prefixes-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-event-table-prefixes-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==52 and b['closed_parent_imports']==['r1_native_event_table_sensor','r1_native_event_table_storage','r1_native_event_table_system']
 callbacks={n for t in c['tables'] for n in t['callbacks'] if n};assert len(callbacks)==37 and callbacks==set(b['newly_exposed_imports'])==set(undefined_symbols(out/'native_event_table_prefixes.o')[0])
 assert sha(out/'event-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'event-source.o')[0]==b['graph_undefined_symbols'] and set(b['graph_undefined_symbols'])==callbacks
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_event_table_prefixes.py')==r['driver_sha256'] and sha(out/'prefix-contracts.json')==b['prefix_contracts_sha256']==r['prefix_contracts_sha256']
 assert r['application_sha256']==sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin') and r['comparisons']==1824 and r['counts']==dict(sensor=768,system=720,storage=336) and r['callback_observations']==1200 and r['free_observations']==912 and r['trace_sha256']=='a3f881d47894d59563ebb655ab02edb4360859cf3a2ff2dd7b634059e0fc603d'
 sections=allocated_sections(out/'native_event_table_prefixes.o');assert [(t['family'],t['address'],len(t['words'])) for t in c['tables']]==[('sensor','0x20006750',17),('system','0x20006e54',16),('storage','0x200066fc',8)] and r['relocated_prefix_bytes']==164
 for t in c['tables']:
  a=int(t['address'],16);size=4*len(t['words']);assert sections[t['section']][2:]==[size,4,hashlib.sha256(bytes(size)).hexdigest()] and not t['full_extent_proven']
  for i,(w,n) in enumerate(zip(t['words'],t['callbacks'])):assert int.from_bytes(data[a-0x200064a8+4*i:a-0x200064a8+4*i+4],'little')==w and (n=='r1_event_callback_%08x'%(w&~1) if w else n is None)
 f=json.loads((out/'callback-frontier.json').read_text());assert f['prefix_contracts_sha256']==sha(out/'prefix-contracts.json') and f['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and {x['source_import'] for x in f['callbacks']}==callbacks and all(not x['body_span_proven'] and not x['body_compiled_in_native_prefix_stage'] for x in f['callbacks'])
 for flag in ['actual_source_dispatch_and_typed_table_relocations','all_observed_prefix_slots_and_writable_rebinding_checked','callbacks_and_free_are_fixtures']:assert r[flag]
 for flag in ['callback_bodies_source_complete','full_table_extents_proven','full_private_frame_history_verified','full_raw_abi_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 assert 'AssertionError' in (out/'pre-native-free-fixture-fix/failure.log').read_text()
 print('Event table prefixes:164 source bytes;1824 dispatch checks;3 anchors close,37 callback bodies exposed;52 main imports')
if __name__=='__main__':audit()
