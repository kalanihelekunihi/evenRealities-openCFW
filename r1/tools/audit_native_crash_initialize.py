#!/usr/bin/env python3
"""Bind crash initializer contracts without promoting fixture evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-crash-initialize';r=json.loads((out/'verification.json').read_text());b=json.loads((BASE/'native-crash-initialize-runtime/report.json').read_text())
 assert r['initializer_comparisons']==1440 and r['status_comparisons']==256 and r['observation_counts']==dict(offset=1440,timestamp=1440,payload=1440,copy=120,snapshot=1440,crc=1440) and r['trace_sha256']=='c8984a76fc6f18766d736f343abae3469595fb687b82331006c533cf7c2c480b'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'native_crash_initialize.o')==r['object_sha256'] and sha(ROOT/'r1/tools/verify_native_crash_initialize.py')==r['driver_sha256'] and sha(BASE/'native-crash-initializer-rea.json')==r['rea_sha256'] and sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin')==r['application_sha256']
 for flag in ['actual_initializer_and_status_bodies','other_callees_are_fixtures','external_frame24_and_saved_r3_halfword_checked','raw_r0_callee_sp_record_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','actual_payload_snapshot_crc_composition_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 e=json.loads((out/'rea-payload-getter.json').read_text())['structuredContent'];n=e['normalized_result'];assert e['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and n['complete'] and n['address']=='0x6abe4' and n['returned_bytes']==20
 app=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert bytes.fromhex(n['bytes_hex'])==app[0x6abe4-0x27000:0x6abf8-0x27000] and n['bytes_hex']=='002803d04ff43871018001487047000054e00120'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=BASE/'native-crash-initialize-runtime/native-crash-initialize-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==25
 assert b['closed_parent_imports']==['r1_health_crash_record_initializer'] and b['newly_exposed_imports']==['r1_crash_record_marker_set','r1_health_crash_snapshot_builder'] and b['canonical_reset_context_reused']
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Crash initialize:1440 cases plus256 status values;736/896 mismatch retained')
if __name__=='__main__':audit()
