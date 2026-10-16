#!/usr/bin/env python3
"""Bind typed provider tables and sensor factories without admitting hardware bodies."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 from audit_source_frontier import section_bytes
 out=BASE/'native-stream-singletons-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==1932 and r['counts']==dict(acc=384,temp=384,workflow=384,open=30,close=30,read=720) and r['observation_counts']==dict(allocate=2688,mode=2192,ring=696,sdk=448,calibrated=90) and r['trace_sha256']=='8e53763ac48c761e96b92b4f9b7fa97368cd9b2b4c587e2c72ea80b85af198d0'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'stream-singletons-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_stream_singletons.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=BASE/'native-stream-singletons'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for name,a in [('acc_ops',0x9a590),('temp_ops',0x9a5a8)]:assert r['provider_table_sha256'][name]==hashlib.sha256(binary[a-0x27000:a-0x27000+12]).hexdigest()
 sections=allocated_sections(BASE/'native-stream-singletons/native_stream_singletons.o')
 for name,a in [('open',0x918fc),('close',0x918f8)]:assert section_bytes(BASE/'native-stream-singletons/native_stream_singletons.o','.text.r1_stream_temperature_'+name)==binary[a-0x27000:a-0x27000+4]
 for name in ['acc','temp']:assert sections['.r1.stream.'+name+'.ops'][:4]==[1,2,12,4]
 for flag in ['actual_five_bodies_object_core_memory_strings_lists','only_allocation_logging_calibrated_temperature_are_fixtures','motion_hardware_providers_not_executed','typed_provider_tables_match_native','raw_r0_callee_sp_registry_object_and_read_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_provider_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-stream-singletons-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==23 and undefined_symbols(out/'stream-singletons-source.o')[0]==b['graph_undefined_symbols'] and set(b['graph_undefined_symbols'])<=set(b['undefined_symbols'])
 assert b['closed_parent_imports']==['r1_native_accelerometer_singleton','r1_native_temperature_singleton'] and b['newly_exposed_imports']==['r1_motion_initialize_entry','r1_motion_stream_close_boundary','r1_motion_thirty_sample_batch_producer','r1_temperature_pair_read_calibrated']
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Stream singletons:1932 cases; typed tables authenticated, four sensor provider gates exposed')
if __name__=='__main__':audit()
