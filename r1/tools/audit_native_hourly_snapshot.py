#!/usr/bin/env python3
"""Authenticate hourly query, source-zero extent and composed snapshot receipt."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-hourly-snapshot';graph=BASE/'native-hourly-snapshot-runtime';r=json.loads((out/'verification.json').read_text());g=json.loads((graph/'verification.json').read_text());b=json.loads((graph/'report.json').read_text())
 assert r['comparisons']==13824 and r['trace_sha256']=='5ca9bcdd659bdb73d0dd821af95d50a879d73b1135471088c5f1e2023de3a776'
 assert sha(out/'report.json')==r['report_sha256']==g['hourly_report_sha256'] and sha(out/'native_hourly_snapshot.o')==r['object_sha256']==g['hourly_object_sha256'] and sha(ROOT/'r1/tools/verify_native_hourly_snapshot.py')==r['driver_sha256']
 for p,h in r['evidence'].items():assert sha(out/p)==h,p
 assert allocated_sections(out/'native_hourly_snapshot.o')['.bss.r1.hourly.accumulators']==[8,3,48,4,hashlib.sha256(b'').hexdigest()] and 0x20007e04<=0x20016648<0x20016648+48<=0x20007e04+0x340b4
 for flag in ['actual_query_body_no_fixtures','raw_r0_callee_sp_table_and_output_ram_checked','output_record_alias_and_fresh_count_checked']:assert r[flag]
 assert r['source_zero_record_bytes']==48
 assert g['comparisons']==23328 and g['observation_counts']==dict(clear=23328,activity=23328,hr=23328,spo2=23328,hrv=23328,query=11304) and g['trace_sha256']=='4c3a33338966cf3ebbcca3198b9503a0d9a4778e46ac6374f06d44f5c0eb9716'
 assert sha(ROOT/'r1/tools/verify_native_hourly_snapshot_graph.py')==g['driver_sha256'] and sha(graph/'report.json')==g['runtime_report_sha256'] and sha(BASE/'native-crash-snapshot/report.json')==g['report_sha256'] and sha(BASE/'native-crash-snapshot/native_crash_snapshot.o')==g['object_sha256'] and sha(BASE/'native-crash-snapshot/rea-snapshot.json')==g['rea_sha256']
 for flag in ['actual_both_snapshot_ranges','actual_hourly_query_and_snapshot_bodies','cache_providers_and_clear_are_fixtures','declared_query_outputs_and_native_pointer_offsets_checked','raw_r0_callee_sp_record_and_cache_ram_checked']:assert g[flag]
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']==g['application_sha256']
 p=json.loads((graph/'raw-frame-probe.json').read_text());assert sha(graph/'raw-frame-probe.json')==g['raw_frame_probe_sha256'] and not p['matched'] and p['different_cases']==g['raw_frame_difference_cases']==23328 and p['no_frame_normalization'] and p['driver_sha256']==g['driver_sha256'] and p['first']['native']!=p['first']['source']
 for receipt,flags in [(r,['producer_lifecycle_proven','full_private_frame_history_verified','instruction_identity','whole_image_complete','hardware_write_executed']),(g,['full_private_frame_history_verified','full_raw_abi_verified','actual_health_provider_composition_verified','instruction_identity','whole_image_complete','hardware_write_executed'])]:
  for flag in flags:assert not receipt[flag]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=graph/'native-hourly-snapshot-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==28
 assert b['closed_parent_imports']==['r1_hr_hour_query'] and b['newly_exposed_imports']==[]
 print('Hourly snapshot:13824 direct and23328 composed cases; raw ABI gate preserved')
if __name__=='__main__':audit()
