#!/usr/bin/env python3
"""Authenticate bounded health settings while retaining a failed-read caller gate."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-settings'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-health-settings-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json');probe=read(rp.parent/'failed-read-frame-probe.json')
 assert r['comparisons']==21056 and r['counts']==dict(handler=10304,get=9216,set=1536) and r['observations_per_side']==119496 and r['trace_sha256']=='4f50a77c272f831b79ca97fc715cb43e7717238691105a420b06b2fd706abfe7' and all(r['lower_observation_counts'].values())
 for flag in ['actual_handler_flag_word_helpers_kv_musl_accessor','event_idle_transport_logging_critical_are_fixtures','handler_workflows_use_successful_cached_reads','direct_helper_failed_read_seed_views_checked','accessor_before_ack_and_raw_requested_comparison_checked','live_event_status_after_setter_and_conditional_timestamp_checked','raw_r0_callee_sp_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['portable_planner_modified','runtime_admission_changed','hardware_write_executed','health_event_delivery_or_persistence_proven','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_health_settings.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'health-settings-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_health_settings_verification.ld')
 assert not probe['matched'] and probe['number']==17 and probe['failed_read_then_fresh_valid_handle'] and not probe['cached_write_ram_matches'] and probe['raw_r0_matches'] and not probe['cross_call_private_frame_history_verified'] and not probe['whole_image_complete'] and probe['driver_sha256']==sha(ROOT/'r1/tools/probe_native_health_settings_frame.py')
 for key in ['report_sha256','object_sha256','layout_sha256','application_sha256']:assert probe[key]==r[key]
 native,source=probe['outputs'];assert native[0]==source[0] and native[2]!=source[2]
 assert native[1][7][:3]==source[1][7][:3]==['write',0x20001000,52] and native[1][7][3]!=source[1][7][3]
 old=rp.parent/'initial-failed-read-probe'
 for p,h in e['initial_failed_read_probe'].items():assert sha(old/p)==h,p
 prior=read(old/'failed-read-frame-probe.json');assert not prior['matched'] and prior['raw_r0_matches'] and prior['outputs'][0][2]==prior['outputs'][1][2] and prior['driver_sha256']==sha(old/'probe_native_health_settings_frame.py')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-health-settings-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==54 and undefined_symbols(rp.parent/'native-health-settings-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'health-settings-source.o')[0]==b['graph_undefined_symbols']
 parent=read(BASE/'native-system-settings-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_health_settings_plan_command'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('83f24',300),('84050',8),('84058',61),('84098',55),('840d0',49),('84104',43),('73798',48),('73868',64)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for a in ['83f24','73868']:assert 'No procedure exists' in str(read(OUT/f'rea-procedure-{a}.json'))
 q=read(OUT/'rea-procedure-73798.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x73798' and d['body']['total_bytes']==44 and d['body']['ranges']==[dict(start='0x73798',end='0x737c3')]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==3 and all(row in rows for row in e['new_ownership_rows']) and sum(int(row['size']) for row in e['new_ownership_rows'])==404
 from audit_source_frontier import section_bytes
 for section,a,n in [('get_ring',0x84058,61),('get_sdk',0x84098,55),('set_ring',0x840d0,49),('set_sdk',0x84104,43)]:assert section_bytes(OUT/'native_health_settings.o','.r1.health.settings.'+section,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['native_code_bytes']==404 and e['new_owned_text_bytes']==208 and e['separate_native_handler'] and e['raw_record_frames_no_defaults'] and e['conditional_timestamp_write_preserved'] and e['failed_read_fresh_handle_private_frame_gate'] and not e['portable_planner_modified'] and not e['runtime_admission_changed'] and not e['health_event_or_persistence_proven'] and not e['whole_image_identity']
 print('Native health settings:21056 bounded cases;404 native+208 text bytes;54 imports;failed-read fresh-handle RAM counterexample retained;private/effect/image gates OPEN')
if __name__=='__main__':audit()
