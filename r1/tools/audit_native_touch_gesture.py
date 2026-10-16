#!/usr/bin/env python3
"""Authenticate complete native gesture control and explicit provider limitations."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-gesture'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-touch-gesture-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==59328 and r['observations_per_side']==546563 and r['trace_sha256']=='532712c43426c0070ebb26a2c7ae473f82fe988db4c5c05cb32c221b51450503'
 assert all(r['lower_observation_counts'][k]>0 for k in ['schedule','marker','flags','tick','config','handle','tx','mode','ring','sdk'])
 for flag in ['actual_native_control_and_canonical_state_aliases','all_lower_effects_are_fixtures','every_event_byte_precedence_and_counter_edges_checked','post_effect_mutations_and_fresh_reads_checked','timestamp_thresholds_and_packet_length_gates_checked','fullword_handle_and_second_fresh_read_checked','raw_r0_r1_r2_r3_callee_sp_and_nonstack_ram_checked','no_native_candidate_execution','independent_pending_and_contact_mode_fixtures']:assert r[flag]
 for flag in ['portable_planner_modified','runtime_admission_changed','hardware_write_executed','ble_delivery_or_reset_proven','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_touch_gesture.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'touch-gesture-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_touch_gesture_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-touch-gesture-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'gesture-state-owners-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==56 and undefined_symbols(rp.parent/'native-touch-gesture-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'touch-gesture-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'gesture-state-owners-source.o')[0]==[]
 parent=read(BASE/'native-touch-task-message-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_touch_gesture_dispatch_boundary'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 old=rp.parent/'pre-independent-pending-fixture'
 for p,h in e['superseded_limited_coverage'].items():assert sha(old/p)==h,p
 prior=read(old/'verification.json');assert prior['comparisons']==59328 and prior['trace_sha256']=='b5c2fc37513513362d59aabc71a75cb3dac57cb2f39005fa8371b0c035761dba' and prior['driver_sha256']==sha(old/'verify_native_touch_gesture.py') and prior['object_sha256']==r['object_sha256']
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('3e938',690),('3ebec',20),('3ebfc',35),('3ec20',29),('3ec40',56),('bfcd8',101),('bfd40',95),('bfc10',101),('bfc78',95),('bff24',99),('bff88',93),('bfe64',98),('bfec8',92),('bfda0',100),('bfe04',94),('bfb40',105),('bfbac',99)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 q=read(OUT/'rea-procedure.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x3e938' and d['body']['total_bytes']==690 and d['body']['ranges']==[dict(start='0x3e938',end='0x3ebe9')]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==690
 from audit_source_frontier import section_bytes
 logs=[('reset_ring',0x3ebfc,35),('reset_sdk',0x3ec20,29),('single_ring',0xbfcd8,101),('single_sdk',0xbfd40,95),('double_ring',0xbfc10,101),('double_sdk',0xbfc78,95),('long_ring',0xbff24,99),('long_sdk',0xbff88,93),('up_ring',0xbfe64,98),('up_sdk',0xbfec8,92),('down_ring',0xbfda0,100),('down_sdk',0xbfe04,94),('release_ring',0xbfb40,105),('release_sdk',0xbfbac,99)]
 for section,a,n in logs:assert section_bytes(OUT/'native_touch_gesture.o','.r1.touch.gesture.'+section,executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
 for section,a,n in [('direction',0x200067c5,1),('count',0x200067cc,2),('time',0x200067dc,4),('up_time',0x200067e0,4),('down_time',0x200067e4,4)]:assert section_bytes(OUT/'native_touch_gesture.o','.r1.touch.gesture.'+section,executable=False)==cold[a-0x200064a8:a-0x200064a8+n]
 assert e['native_code_bytes']==690 and e['new_owned_text_bytes']==1236 and e['new_owned_ram_bytes']==15 and e['existing_contact_and_context_fields_reused'] and e['service_context_fields_need_eventual_alias'] and e['all_lower_effects_are_fixtures'] and not e['portable_planner_modified'] and not e['runtime_admission_changed'] and not e['whole_image_identity']
 print('Native gesture dispatcher authenticated:59328 cases;690 native+1251 owned bytes;canonical state;56 imports;effect/private/context/image gates retained')
if __name__=='__main__':audit()
