#!/usr/bin/env python3
"""Authenticate BLE encoder source and explicitly bounded fixture comparisons."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-ble-message'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-ble-message-runtime/report.json';b=read(rp)
 assert r['comparisons']==14112 and r['observations_per_side']==56526 and r['trace_sha256']=='52c18cfd2d83d01d250432cc2433c711461d8b52adf77514e1f510919fa48a93'
 for flag in ['actual_source_memory_move','source_log_texts_match','allocation_rounding_and_wrap_checked','fresh_queue_thread_and_local_message_reads_checked','provider_register_clobbers_checked','only_allocation_queue_flags_logging_are_fixtures','private_queue_item_pointer_not_compared','raw_r0_callee_sp_and_observed_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['whole_allocator_queue_or_rtos_graph_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_ble_message.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['message_object_sha256']==sha(rp.parent/'ble-message-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_ble_message_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['helper_object_sha256']==sha(rp.parent/'message-helpers-source.o') and b['linked_sha256']==sha(rp.parent/'native-ble-message-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==71 and undefined_symbols(rp.parent/'native-ble-message-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'ble-message-source.o')[0]==b['message_undefined_symbols']==['nrf_log_frontend_std_0','osMessageQueuePut','osThreadFlagsSet','pvPortMalloc','r1_structured_log_format','r1_structured_log_mode_get','vPortFree']
 parent=read(BASE/'native-protocol-control-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_ble_thread_message_encode'] and not b['newly_exposed_imports']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in e['byte_read_sizes'].items():
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 q=read(OUT/'rea-33850.json')['structuredContent'];assert q['normalized_result']['body']['total_bytes']==306
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==306
 from audit_source_frontier import section_bytes
 obj=OUT/'native_ble_message.o';total=4
 for i,a in enumerate([0x33990,0x339bc,0x339e4,0x33a14,0x33a3c,0x33a64,0x33a88,0x33ab8]):
  n=e['byte_read_sizes'][f'{a:x}'];total+=n;assert section_bytes(obj,f'.r1.ble.message.log{i}',executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();offset=0x20006574-0x200064a8
 assert section_bytes(obj,'.r1.ble.message.queue',executable=False)==cold[offset:offset+4]==bytes(4) and total==e['new_owned_data_bytes']==334
 assert not e['private_queue_item_pointer_identity_verified'] and not e['whole_allocator_queue_graph_executed'] and not e['whole_image_identity']
 cr=rp.parent/'control-graph-report.json';cb=read(cr);g=read(rp.parent/'control-graph-verification.json')
 assert g['comparisons']==8344 and g['observations_per_side']==29647 and g['trace_sha256']=='a744f6cdbfcac2a45acc862c618d84962ef4656487e60b5bfd48a8f9abd029c3'
 assert g['actual_ble_encoder_and_memory_move'] and g['actual_source_payload_flag_checked_phone_helpers'] and g['actual_setting_plan_to_report_setter'] and g['only_logging_transport_role_os_allocator_queue_are_fixtures'] and g['no_native_candidate_execution'] and not g['whole_dispatch_allocator_queue_or_rtos_graph_executed'] and not g['whole_image_complete']
 assert g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_ble_control_graph.py') and g['runtime_report_sha256']==sha(cr) and g['object_sha256']==cb['graph_object_sha256']==sha(rp.parent/'ble-control-graph-source.o') and g['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_ble_control_graph_verification.ld') and g['application_sha256']==r['application_sha256']
 for p,h in cb['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in cb[group].items():assert sha(BASE/p)==h,p
 assert len(cb['undefined_symbols'])==11 and undefined_symbols(rp.parent/'ble-control-graph-source.o')[0]==cb['undefined_symbols']
 gate=e['same_name_distinct_body_gate'];assert gate['unresolved_entry']=='0x00033dbc' and gate['exclude_symbol_only_match']
 assert next(x for x in rows if x['entry']=='0x00033dbc')['upstream_symbol']=='r1_ble_thread_message_encode'
 print('BLE encoder authenticated:14112 comparisons;306 native bytes;334 owned data bytes;71 imports;allocator/queue graph, ABI and image gates open')
if __name__=='__main__':audit()
