#!/usr/bin/env python3
"""Bind shared task message sender and actual timer caller, retaining RTOS gates."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-task-message'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-touch-task-message-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==12672 and r['counts']==dict(sender=9216,timer=3072,workflow=384) and r['observations_per_side']==52665 and r['trace_sha256']=='346e1d2a0f1617203f62ae25fccbf5cb5fcb2218474b8dab7db8bf3ff1c1053e'
 for flag in ['actual_sender_timer_callback_and_attributed_clear','only_queue_flags_logging_are_fixtures','null_message_only_controlled_queue_boundary_fixture','fresh_thread_after_put_and_boolean_result_checked','two_call_queue_mutation_workflows_checked','callback_source14bytes_at_native_verification_vma','raw_r0_callee_sp_and_nonstack_ram_checked']:assert r[flag]
 for flag in ['portable_planner_modified','runtime_admission_changed','hardware_write_executed','rtos_delivery_proven','shared_task_context_complete','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_touch_task_message.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'touch-task-message-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_touch_task_message_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-touch-task-message-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'message-timer-helpers-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==57 and undefined_symbols(rp.parent/'native-touch-task-message-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'touch-task-message-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'message-timer-helpers-source.o')[0]==['r1_touch_task_message_boundary']
 parent=read(BASE/'native-touch-release-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_touch_task_message_boundary'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('93514',150),('935ac',12),('935b8',42),('935e4',36),('93608',17),('9361c',11)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 q=read(OUT/'rea-procedure.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x93514' and d['body']['total_bytes']==150 and d['body']['ranges']==[dict(start='0x93514',end='0x935a9')]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==150
 from audit_source_frontier import section_bytes
 for section,a,n in [('.r1.touch.task.null_ring',0x935b8,42),('.r1.touch.task.null_sdk',0x935e4,36),('.r1.touch.task.missed_ring',0x93608,17),('.r1.touch.task.missed_sdk',0x9361c,11)]:assert section_bytes(OUT/'native_touch_task_message.o',section,executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes();assert section_bytes(OUT/'native_touch_task_message.o','.r1.touch.task.queue',executable=False)==cold[0x20006670-0x200064a8:0x20006674-0x200064a8]==bytes(4)
 assert e['native_code_bytes']==150 and e['new_owned_text_bytes']==106 and e['new_owned_ram_bytes']==4 and e['shared_context_queue_alias_required'] and e['reuses_existing_thread_cell'] and e['queue_success_boolean_result'] and not e['portable_planner_modified'] and not e['runtime_admission_changed'] and not e['rtos_delivery_proven'] and not e['whole_image_identity']
 print('Shared task sender authenticated:12672 cases;150 native+110 owned bytes;actual timer/clear/sender;57 imports;RTOS/context/private/image gates retained')
if __name__=='__main__':audit()
