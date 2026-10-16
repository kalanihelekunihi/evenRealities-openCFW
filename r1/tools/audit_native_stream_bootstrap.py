#!/usr/bin/env python3
"""Bind native stream contracts, shared providers and remaining runtime gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-stream-bootstrap-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==2880 and r['counts']==dict(initialize=480,create=480,wake=480,enable=480,tick=480,keepalive=480) and r['observation_counts']==dict(allocate=960,tick=960,wake=832) and r['matching_fatal_faults']==480 and r['trace_sha256']=='12cacf2e50662b9a2cf75fd6c8adadaed903caf550ad555cf7c817f31e4b7cd8'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'stream-bootstrap-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_stream_bootstrap.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=BASE/'native-stream-bootstrap'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for flag in ['actual_six_bodies_lists_and_cmsis_dispatch','allocator_clock_leaf_wake_callbacks_are_fixtures','raw_r0_callee_sp_housekeeping_list_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','actual_allocator_clock_scheduler_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 assert r['keepalive_instruction_bytes']==2 and r['source_zero_bytes']==52
 sections=allocated_sections(BASE/'native-stream-bootstrap/native_stream_bootstrap.o')
 for name,size in [('housekeeping',48),('tick_getter',4)]:assert sections['.bss.r1.stream.'+name]==[8,3,size,4,hashlib.sha256(b'').hexdigest()]
 assert 0x20007e04<=0x2001a2b4<0x2001a2b8<=0x2001a2bc<0x2001a2ec<=0x20007e04+0x340b4
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-stream-bootstrap-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==22 and undefined_symbols(out/'stream-bootstrap-source.o')[0]==[]
 assert b['closed_parent_imports']==['r1_native_stream_initialize'] and b['newly_exposed_imports']==[]
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Stream bootstrap:2880 cases,480 matching fatal faults; existing list/CMSIS reuse authenticated')
if __name__=='__main__':audit()
