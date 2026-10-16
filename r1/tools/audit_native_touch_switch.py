#!/usr/bin/env python3
"""Authenticate native touch command separately from portable policy admission."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-switch'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-touch-switch-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==16128 and r['counts']==dict(null=3584,unknown=5984,phone=3286,glasses=3274) and r['observations_per_side']==37801 and r['trace_sha256']=='3fe441839019a2d6b7a10d2d7460979e31cdda6cc44d8cd347d39b219ecf8390'
 for flag in ['actual_accessor_checked_send_and_ack_header','only_lower_response_touch_services_and_logging_are_fixtures','response_precedes_selector_read','fresh_switch_values_after_logs_checked','response_mutation_preserves_saved_word','raw_r0_r1_r2_r3_callee_sp_nonstack_ram_checked','short_backing_only_mapped_fixture','no_native_candidate_execution']:assert r[flag]
 for flag in ['portable_planner_modified','runtime_admission_changed','touch_service_effects_implemented','hardware_write_executed','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_touch_switch.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'touch-switch-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_touch_switch_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-touch-switch-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'touch-switch-helpers-source.o') and b['checked_object_sha256']==sha(rp.parent/'touch-checked-source.o') and b['serial_object_sha256']==sha(BASE/'native-protocol-serial/native_protocol_serial.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==58 and undefined_symbols(rp.parent/'native-touch-switch-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'touch-switch-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'touch-switch-helpers-source.o')[0]==[]
 parent=read(BASE/'native-device-id-reader-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_touch_switch_handler_plan_decode'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_service_touch_close','r1_service_touch_open']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('84874',184),('8492c',8),('84934',55),('8496c',49),('849a0',57),('849dc',51)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 assert 'No procedure exists' in str(read(OUT/'rea-procedure.json')) and e['procedure_metadata_missing']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==184
 from audit_source_frontier import section_bytes
 for name,a,n in [('phone_ring',0x84934,55),('phone_sdk',0x8496c,49),('glasses_ring',0x849a0,57),('glasses_sdk',0x849dc,51)]:assert section_bytes(OUT/'native_touch_switch.o','.r1.touch.switch.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['native_code_bytes']==184 and e['new_owned_text_bytes']==212 and e['separate_native_handler_symbol'] and e['main_partial_alias_only'] and not e['portable_planner_modified'] and not e['runtime_admission_changed'] and not e['touch_service_effects_implemented'] and not e['whole_image_identity']
 print('Native touch-switch authenticated:16128 cases;184 native+212 text bytes;actual accessor/checked/header;58 imports;planner/hardware/private/image gates retained')
if __name__=='__main__':audit()
