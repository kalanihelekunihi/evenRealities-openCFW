#!/usr/bin/env python3
"""Authenticate both snapshot ranges while retaining raw ABI counterexamples."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-crash-snapshot';r=json.loads((out/'verification.json').read_text());b=json.loads((BASE/'native-crash-snapshot-runtime/report.json').read_text());probe=json.loads((out/'raw-frame-probe.json').read_text())
 assert r['comparisons']==23328 and r['observation_counts']==dict(clear=23328,activity=23328,hr=23328,spo2=23328,hrv=23328,query=11304) and r['trace_sha256']=='c6cbed58aacbd0731e6e18b7817954c5faa54ea617649f78037aa9b49808853d'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'native_crash_snapshot.o')==r['object_sha256'] and sha(ROOT/'r1/tools/verify_native_crash_snapshot.py')==r['driver_sha256']==probe['driver_sha256'] and sha(out/'rea-snapshot.json')==r['rea_sha256'] and sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin')==r['application_sha256']
 for flag in ['actual_both_snapshot_ranges','providers_and_clear_are_fixtures','declared_query_outputs_and_native_pointer_offsets_checked','raw_r0_callee_sp_record_and_cache_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','actual_health_provider_composition_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 assert sha(out/'raw-frame-probe.json')==r['raw_frame_probe_sha256'] and not probe['matched'] and probe['different_cases']==r['raw_frame_difference_cases']>0 and probe['declared_query_outputs_and_record_cache_ram_match'] and probe['no_frame_normalization'] and probe['first']['native']!=probe['first']['source']
 old=json.loads((out/'pre-raw-probe/verification.json').read_text());assert sha(out/'pre-raw-probe/verify_native_crash_snapshot.py')==old['driver_sha256'] and old['trace_sha256']==r['trace_sha256'] and old['object_sha256']==r['object_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=BASE/'native-crash-snapshot-runtime/native-crash-snapshot-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==29
 assert b['closed_parent_imports']==['r1_health_crash_snapshot_builder'] and b['newly_exposed_imports']==['r1_activity_daily_cache_accessor','r1_hr_daily_cache_accessor','r1_hr_hour_query','r1_hrv_daily_cache_accessor','r1_spo2_daily_cache_accessor']
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Crash snapshot:23328 bounded cases; raw scratch/frame history remains open')
if __name__=='__main__':audit()
