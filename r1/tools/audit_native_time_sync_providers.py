#!/usr/bin/env python3
"""Authenticate query saved-byte semantics and timeout callback source."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-time-sync-providers'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-time-sync-providers-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==22368 and r['counts']==dict(query_fixture=20736,query_cached=480,timeout=1152) and r['observations_per_side']==23760 and r['trace_sha256']=='7700383d85c83525181f3e1edf4c67d786bfb3fd3032fab7f089ad45a106913d'
 for flag in ['actual_cached_read_musl_and_phone_accessor','source_cold_classes_handles_match','query_failure_retains_incoming_r3_byte','raw_r0_r3_callee_sp_and_nonstack_ram_checked','ble_enqueue_and_critical_callbacks_are_fixtures','post_getter_and_critical_mutations_are_explicit','no_native_candidate_execution']:assert r[flag]
 for flag in ['runtime_admission_changed','hardware_write_executed','cross_call_private_frame_history_verified','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_time_sync_providers.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'time-sync-providers-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_time_sync_providers_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-time-sync-providers-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'query-helpers-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==60 and undefined_symbols(rp.parent/'native-time-sync-providers-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'time-sync-providers-source.o')[0]==b['graph_undefined_symbols']==['r1_ble_thread_message_encode'] and undefined_symbols(rp.parent/'query-helpers-source.o')[0]==[]
 parent=read(BASE/'native-time-sync-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_nv_recovery_needed_query_boundary','r1_protocol_time_timeout_callback'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('7bb20',36),('84c82',22)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 assert 'No procedure exists' in str(read(OUT/'rea-procedure-7bb20.json')) and e['query_procedure_metadata_missing']
 q=read(OUT/'rea-procedure-84c82.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x84c82' and d['body']['total_bytes']==22 and d['body']['ranges']==[dict(start='0x84c82',end='0x84c97')] and e['timeout_procedure_metadata_observed']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==22
 assert e['native_code_bytes']==54 and e['no_new_data_owners'] and e['query_uses_incoming_r3_on_failed_read'] and not e['runtime_admission_changed'] and not e['cross_call_private_history_verified'] and not e['whole_image_identity']
 print('Time query/timeout authenticated:22368 cases;32 supplemental+22 locked native bytes;60 imports;actual cached-read/musl;private caller history/image gates retained')
if __name__=='__main__':audit()
