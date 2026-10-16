#!/usr/bin/env python3
"""Authenticate motion adapters while retaining licensed provider and NV gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-motion-stream-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==6425 and r['counts']==dict(initialize=768,entry=768,interrupt=768,fifo=768,close=5,bypass=256,calibration=180,batch=2912) and r['observation_counts']==dict(probe=512,open=640,interrupt=256,fifo=3137,nv=2581,policy=30270,tick=2401) and r['trace_sha256']=='ef7aef8e535acbf11469c5c1be3055a35fa71e43efd74c736581e58b5de89a70'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'motion-stream-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_motion_stream.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=BASE/'native-motion-stream'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for flag in ['actual_eight_entries_batch_adjustment_and_shared_tick_selector','only_selected_sensor_probe_nv_read_clock_are_fixtures','raw_r0_batch_restored_r2_r3_callee_sp_and_ram_checked','exact_nv_scratch_and_offset_api_pointer_coordinates_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_nv_clock_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 cold=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(cold)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317';data=cold.read_bytes()
 sections=allocated_sections(BASE/'native-motion-stream/native_motion_stream.o')
 for name,a,size in [('selected',0x200076ac,4),('calib.bypass',0x20006c35,1)]:assert sections['.r1.motion.'+name][2]==size and sections['.r1.motion.'+name][4]==hashlib.sha256(bytes(size)).hexdigest() and data[a-0x200064a8:a-0x200064a8+size]==bytes(size)
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-motion-stream-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==20 and undefined_symbols(out/'motion-stream-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_motion_initialize_entry','r1_motion_stream_close_boundary','r1_motion_thirty_sample_batch_producer','r1_native_motion_interrupt'] and b['newly_exposed_imports']==['r1_motion_probe_and_select_provider']
 old=out/'pre-policy-call-boundary';unit=json.loads((old/'unit-report.json').read_text());historical=json.loads((old/'report.json').read_text());probe=json.loads((old/'counterexample.json').read_text())
 assert sha(old/'native_motion_stream.c')==unit['units'][0]['source_sha256'] and sha(old/'native_motion_stream.o')==unit['units'][0]['object_sha256'] and sha(old/'motion-stream-source.o')==historical['graph_object_sha256'] and sha(old/'native-motion-stream-runtime.o')==historical['linked_sha256'] and sha(old/'unit-report.json')==historical['provider_reports']['native-motion-stream/report.json'] and sha(old/'verify_native_motion_stream.py')==probe['driver_sha256']
 assert probe['outputs_without_trace_match'] and probe['native_policy_calls']==1 and probe['source_policy_calls']==0
 a=list(probe['native']);c=list(probe['source']);a.pop(2);c.pop(2);assert a==c
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Motion stream:6425 cases; real selection/probe/NV/clock execution remains gated')
if __name__=='__main__':audit()
