#!/usr/bin/env python3
"""Bind shared cache layouts, native resets and preserved raw-return repair."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_health_cache_runtime import symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-health-cache-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==960 and r['counts']==dict(getter=960,reset=960,workflow=480) and r['native_clear_calls']==2880 and r['trace_sha256']=='c74beaba0c5aba473ee1435a826fa79eb53e0f8134c7605c339c830ac68953f8'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'health-cache-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_health_cache.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():assert sha(BASE/'native-health-cache'/p)==h,p
 for p in (BASE/'native-health-cache').glob('rea-*.json'):
  n=json.loads(p.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for flag in ['actual_eight_bodies_and_memory_clear','no_provider_fixtures','canonical_metadata_addresses_and_nonduplicate_cache_state_checked','raw_r0_callee_sp_full_cache_region_checked']:assert r[flag]
 for flag in ['producer_service_initialization_proven','full_private_frame_history_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-health-cache-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==24 and undefined_symbols(out/'health-cache-source.o')[0]==[]
 assert b['closed_parent_imports']==['r1_activity_daily_cache_accessor','r1_hr_daily_cache_accessor','r1_hrv_daily_cache_accessor','r1_spo2_daily_cache_accessor'] and b['newly_exposed_imports']==[] and b['new_source_zero_bytes']==888 and b['existing_metadata_bytes_reused']==24 and b['consolidated_cache_bytes']==912 and b['canonical_metadata_reused']
 s=symbols(linked);sections=allocated_sections(linked)
 for name,layout in b['cache_layout'].items():
  base=s['r1_cache_'+name][0];assert s['r1_daily_'+name+'_offset'][0]==base+layout['offset_at'] and s['r1_daily_'+name+'_timestamp'][0]==base+layout['timestamp_at'] and sections[layout['section']][2]==layout['bytes'] and sections[layout['section']][4]==hashlib.sha256(bytes(layout['bytes'])).hexdigest()
 old=out/'pre-clear-return-fix';unit=json.loads((old/'unit-report.json').read_text());runtime=json.loads((old/'runtime-report.json').read_text())
 assert sha(old/'native_health_cache.c')==unit['units'][0]['source_sha256'] and sha(old/'native_health_cache.o')==unit['units'][0]['object_sha256'] and sha(old/'health-cache-source.o')==runtime['graph_object_sha256'] and sha(old/'native-health-cache-runtime.o')==runtime['linked_sha256'] and sha(old/'unit-report.json')==runtime['provider_reports']['native-health-cache/report.json']
 assert sha(old/'verify_native_health_cache.py')==r['driver_sha256'] and '536963332' in (old/'failure.log').read_text() and '536962756' in (old/'failure.log').read_text()
 print('Health cache:960 workflows with2880 actual clears; metadata shared, raw-return repair retained')
if __name__=='__main__':audit()
