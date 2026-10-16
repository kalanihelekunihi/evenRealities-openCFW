#!/usr/bin/env python3
"""Authenticate client masks/task post and caller without claiming release effects."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-touch-services'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-touch-services-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==42408 and r['counts']==dict(open=20304,close=20304,post=120,command=1680) and r['observations_per_side']==86021 and r['trace_sha256']=='807812b40fc098cf2f05dea998bf19f234594bbc539f9319cc361adbba037e7c'
 for flag in ['actual_touch_services_task_post_and_command_accessor_checked_header','only_release_flags_response_logging_are_fixtures','all_low8_shift_counts_and_fullword_aliases_checked','fresh_client_and_thread_reads_after_effects_checked','native_pre_or_open_return_word_checked','raw_r0_callee_sp_nonstack_ram_and_caller_r1_r2_r3_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['portable_planner_modified','runtime_admission_changed','hardware_write_executed','synthetic_release_effect_implemented','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_touch_services.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'touch-services-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_touch_services_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-touch-services-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==57 and undefined_symbols(rp.parent/'native-touch-services-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'touch-services-source.o')[0]==b['graph_undefined_symbols']
 parent=read(BASE/'native-touch-switch-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_service_touch_close','r1_service_touch_open'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_touch_synthetic_release_boundary']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('8e6a0',100),('8e704',4),('8e708',37),('8e730',8),('8e738',31),('8e7d0',94),('8e830',4),('8e834',36),('8e858',8),('8e860',30),('93504',16)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for a,n,end in [('8e6a0',100,'8e703'),('8e7d0',94,'8e82d'),('93504',10,'9350d')]:
  q=read(OUT/f'rea-procedure-{a}.json')['structuredContent'];d=q['normalized_result'];assert q['provider']['id']=='ghidra' and d['entrypoint']=='0x'+a and d['body']['total_bytes']==n and d['body']['ranges']==[dict(start='0x'+a,end='0x'+end)]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==3 and all(row in rows for row in e['new_ownership_rows']) and sum(int(row['size']) for row in e['new_ownership_rows'])==204
 from audit_source_frontier import section_bytes
 for section,a,n in [('.r1.touch.close.ring',0x8e708,37),('.r1.touch.close.sdk',0x8e738,31),('.r1.touch.open.ring',0x8e834,36),('.r1.touch.open.sdk',0x8e860,30)]:assert section_bytes(OUT/'native_touch_services.o',section,executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
 for section,a in [('.r1.touch.clients',0x200067d8),('.r1.touch.thread',0x2000666c)]:assert section_bytes(OUT/'native_touch_services.o',section,executable=False)==cold[a-0x200064a8:a-0x200064a8+4]==bytes(4)
 assert e['native_code_bytes']==204 and e['new_owned_text_bytes']==134 and e['new_owned_ram_bytes']==8 and e['context_fields_need_eventual_alias'] and e['register_shift_low8_semantics_preserved'] and e['open_returns_pre_or_word'] and not e['portable_planner_modified'] and not e['runtime_admission_changed'] and not e['synthetic_release_effect_implemented'] and not e['whole_image_identity']
 print('Touch client services authenticated:42408 cases;204 native+142 owned bytes;actual services/task-post/caller;57 imports;release/context/private/image gates retained')
if __name__=='__main__':audit()
