#!/usr/bin/env python3
"""Authenticate stream object contracts without implying singleton closure."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-stream-objects-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==40960 and r['counts']==dict(create=10240,insert=10240,lookup=10240,flag=10240) and r['observation_counts']==dict(allocate=19312,mode=24464,ring=7080,sdk=4504) and r['matching_fatal_faults']==4192 and r['trace_sha256']=='a73b8b8faf140ec1cbf0c681d1ce86e3a427eb086b5e9cac9f7505a8fd13436f'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'stream-objects-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_stream_objects.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=BASE/'native-stream-objects'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for flag in ['actual_four_bodies_memory_strings_and_lists','only_allocator_and_logging_are_fixtures','low8_name_length_full_sample_guard_node_failure_and_lookup_checked','raw_r0_callee_sp_registry_and_object_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_heap_logging_sensor_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 assert r['source_zero_registry_bytes']==12 and allocated_sections(BASE/'native-stream-objects/native_stream_objects.o')['.bss.r1.stream.object_registry']==[8,3,12,4,hashlib.sha256(b'').hexdigest()] and 0x20007e04<=0x2001a1b0<0x2001a1bc<=0x20007e04+0x340b4
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-stream-objects-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==21 and undefined_symbols(out/'stream-objects-source.o')[0]==b['graph_undefined_symbols'] and set(b['graph_undefined_symbols'])<=set(b['undefined_symbols'])
 assert b['closed_parent_imports']==[] and b['newly_exposed_imports']==[]
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Stream objects:40960 cases; shared constructor/registry ready, singleton imports remain open')
if __name__=='__main__':audit()
