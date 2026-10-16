#!/usr/bin/env python3
"""Authenticate composed crash providers and the preserved call-frame repair."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-crash-payload-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text());bridge=BASE/'native-crash-initialize-bridge';v=json.loads((bridge/'verification.json').read_text())
 assert r['initializer_comparisons']==2160 and r['getter_comparisons']==24 and r['observation_counts']==dict(timestamp=2160,payload=2184,snapshot=2160,query=1440,crc=2160,copy=0) and r['trace_sha256']=='adb73ee0f376bd0bc3b3cb12017998e6c0d86a6395b1a51e924301ec39279c8d'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'crash-initialize-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_crash_payload.py')==r['driver_sha256'] and sha(BASE/'native-crash-payload/rea-getter.json')==r['evidence_sha256']
 for flag in ['actual_initializer_snapshot_caches_query_status_offset_crc_and_payload','only_timestamp_backend_is_fixture','payload_advertises736_and_copy896_gate_unreached','raw_r0_restored_r3_callee_sp_record_cache_payload_ram_checked']:assert r[flag]
 for flag in ['producer_lifecycle_proven','full_private_frame_history_verified','full_raw_abi_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 assert v['initializer_comparisons']==1440 and v['status_comparisons']==256 and v['observation_counts']==dict(offset=1440,timestamp=1440,payload=1440,copy=120,snapshot=1440,crc=1440) and v['trace_sha256']=='c8984a76fc6f18766d736f343abae3469595fb687b82331006c533cf7c2c480b'
 for flag in ['actual_initializer_and_status_bodies','other_callees_are_fixtures','external_frame24_and_saved_r3_halfword_checked','raw_r0_callee_sp_record_ram_checked']:assert v[flag]
 for flag in ['full_private_frame_history_verified','actual_payload_snapshot_crc_composition_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not v[flag]
 assert sha(bridge/'report.json')==v['report_sha256'] and sha(bridge/'native_crash_initialize_bridge.o')==v['object_sha256'] and sha(ROOT/'r1/tools/verify_native_crash_bridge.py')==v['driver_sha256'] and sha(BASE/'native-crash-initialize/native_crash_initialize.o')==v['status_provider_object_sha256'] and sha(BASE/'native-crash-initialize/report.json')==v['status_provider_report_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']==v['application_sha256']
 payload=BASE/'native-crash-payload/native_crash_payload.o';assert allocated_sections(payload)['.bss.r1.crash.payload']==[8,3,736,4,hashlib.sha256(b'').hexdigest()] and 0x20007e04<=0x2001e054<0x2001e054+736<=0x20007e04+0x340b4
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-crash-payload-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==23 and undefined_symbols(out/'crash-initialize-source.o')[0]==[]
 parent=BASE/'native-health-cache-runtime/native-health-cache-runtime.o';weak=out/'parent-weak-initializer.o';assert sha(weak)==b['parent_transformed_sha256'] and allocated_sections(parent)==allocated_sections(weak)
 old_nm=subprocess.check_output(['arm-none-eabi-nm','-S',str(parent)],text=True).splitlines();new_nm=subprocess.check_output(['arm-none-eabi-nm','-S',str(weak)],text=True).splitlines();assert [line.replace(' T r1_health_crash_record_initializer',' W r1_health_crash_record_initializer') for line in old_nm]==new_nm
 assert b['closed_parent_imports']==['r1_crash_record_marker_set'] and b['newly_exposed_imports']==[] and b['parent_allocated_sections_unchanged']
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 old=out/'pre-snapshot-frame-fix';historical=json.loads((old/'report.json').read_text());assert sha(old/'crash-initialize-source.o')==historical['graph_object_sha256'] and sha(old/'native-crash-payload-runtime.o')==historical['linked_sha256'] and sha(old/'build_native_crash_payload_runtime.py')==historical['inputs']['r1/tools/build_native_crash_payload_runtime.py'] and sha(old/'verify_native_crash_payload.py')==r['driver_sha256']
 log=(old/'failure.log').read_text();assert '537120720' in log and '537120704' in log
 print('Crash graph:2160 composed,24 getter and1440 bridge cases; native snapshot pointer repaired')
if __name__=='__main__':audit()
