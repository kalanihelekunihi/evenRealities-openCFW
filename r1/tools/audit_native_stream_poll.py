#!/usr/bin/env python3
"""Bind native timer polling and preserve scheduler/ABI evidence gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-stream-poll-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==23328 and r['counts']==dict(poll=10368,expire=2592,remaining=2592,stop=2592,release=2592,elapsed=2592) and r['observation_counts']==dict(tick=19008,callback=1216,free=2520) and r['matching_faults']==3456 and r['trace_sha256']=='04861be03a49e214c3136b43cfa982dd35d4fbc1104d7115176838bb48e3ff9d'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'stream-poll-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_stream_poll.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=BASE/'native-stream-poll'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for flag in ['actual_poll_expire_remaining_stop_release_elapsed_unlink_and_lists','only_clock_timer_callback_free_are_fixtures','restart_fresh_flags_signed_repeat_wrap_and_500_boundary_checked','raw_r0_callee_sp_housekeeping_list_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_clock_allocator_scheduler_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-stream-poll-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==21 and undefined_symbols(out/'stream-poll-source.o')[0]==[]
 assert b['closed_parent_imports']==['r1_native_sensor_timer_poll'] and b['newly_exposed_imports']==[]
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Stream poll:23328 cases,3456 matching faults; callback and runtime gates explicit')
if __name__=='__main__':audit()
