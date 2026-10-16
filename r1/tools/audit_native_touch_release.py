#!/usr/bin/env python3
"""Bind synthetic release and callback while keeping gesture/task effects open."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-release'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-touch-release-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==70656 and r['counts']==dict(release=2160,all_pairs=65536,timer=80,close=1440,command=1440) and r['observations_per_side']==222244 and r['trace_sha256']=='d89b3504b259f3973e59a6415b33d82c13842854d7a4811f721310c7c573469c'
 for flag in ['actual_release_callback_clear_services_and_command_graph','all_coordinate_byte_pairs_checked','only_cancel_gesture_message_flags_response_logging_are_fixtures','actual_attributed_clear_with_native_end_pointer_result','callback_source14bytes_at_native_verification_vma','caller_gesture_private_pointer_values_not_compared','raw_r0_callee_sp_nonstack_ram_and_command_r1_r2_r3_checked']:assert r[flag]
 for flag in ['portable_planner_modified','runtime_admission_changed','hardware_write_executed','gesture_and_task_message_effects_implemented','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_touch_release.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'touch-release-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_touch_release_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-touch-release-runtime.o') and b['memory_object_sha256']==sha(rp.parent/'release-memory-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==58 and undefined_symbols(rp.parent/'native-touch-release-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'touch-release-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'release-memory-source.o')[0]==[]
 parent=read(BASE/'native-touch-services-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_touch_synthetic_release_boundary'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_touch_gesture_dispatch_boundary','r1_touch_task_message_boundary']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('93424',180),('934d8',12),('934e4',30)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for a,n,end in [('93424',180,'934d7'),('934e4',30,'93501')]:
  q=read(OUT/f'rea-procedure-{a}.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x'+a and d['body']['total_bytes']==n and d['body']['ranges']==[dict(start='0x'+a,end='0x'+end)]
 assert 'No procedure exists' in str(read(OUT/'rea-procedure-934d8.json'))
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==2 and all(row in rows for row in e['new_ownership_rows']) and sum(int(row['size']) for row in e['new_ownership_rows'])==210
 from audit_source_frontier import section_bytes
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
 for section,a in [('.r1.touch.timer_pending',0x200067c4),('.r1.touch.synthetic_flag',0x200067c6)]:assert section_bytes(OUT/'native_touch_release.o',section,executable=False)==cold[a-0x200064a8:a-0x200064a8+1]==bytes(1)
 assert section_bytes(OUT/'native_touch_release.o','.r1.touch.contact',executable=False)==bytes(100) and 0x20007e04<=0x20016a60<0x20016a60+100<=0x2003beb8
 assert e['native_code_bytes']==210 and e['new_owned_ram_bytes']==102 and e['complete_cleared_contact_span_owned'] and e['service_context_flags_need_eventual_alias'] and e['callback_fixed_vma_verification_only'] and not e['portable_planner_modified'] and not e['runtime_admission_changed'] and not e['gesture_and_task_message_effects_implemented'] and not e['whole_image_identity']
 print('Synthetic touch release authenticated:70656 cases;210 native+102 source-state bytes;actual clear/callback/services/caller;58 imports;gesture/task/context/private/image gates retained')
if __name__=='__main__':audit()
