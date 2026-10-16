#!/usr/bin/env python3
"""Bind native time-command control-flow evidence without admitting recovery."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-time-sync-command'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-time-sync-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==8192 and r['counts']==dict(null=1920,query=4704,report=1568) and r['observations_per_side']==74832 and r['trace_sha256']=='6e9b34c8fe6f6bb78a042f31247d6726a7f6b8461f6a981115c979686bcb16d4'
 for flag in ['actual_packet_accessor','all_lower_effects_are_fixtures','explicit_post_call_mutations','event_bytes_and_fresh_sequence_checked','cancellation_before_null_accessor_checked','short_backing_only_mapped_fixture','raw_r0_callee_sp_and_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['runtime_admission_changed','hardware_write_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_time_sync.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'time-sync-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_time_sync_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-time-sync-runtime.o') and b['accessor_object_sha256']==sha(rp.parent/'accessor-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==62 and undefined_symbols(rp.parent/'native-time-sync-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'time-sync-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'accessor-source.o')[0]==[]
 parent=read(BASE/'native-nv-recovery-dispatch-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_protocol_command_000846dc'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_nv_recovery_needed_query_boundary','r1_protocol_time_timeout_callback']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('846dc',224),('847bc',12),('847c8',40),('847f0',34),('84814',40),('8483c',34)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 assert 'No procedure exists' in str(read(OUT/'rea-procedure.json')) and e['missing_ghidra_procedure_metadata']
 from audit_source_frontier import section_bytes
 for name,a in [('lost_ring',0x847c8),('lost_sdk',0x847f0),('valid_ring',0x84814),('valid_sdk',0x8483c)]:
  data=section_bytes(OUT/'native_time_sync_command.o','.r1.time.sync.'+name,executable=False);assert data==raw[a-0x27000:a-0x27000+len(data)] and data[-1:]==b'\0'
 assert e['native_code_bytes']==224 and e['new_ownership_rows']==[] and e['build_only_control_flow'] and not e['runtime_admission_changed'] and not e['identity_table_copied'] and not e['private_frame_history_verified'] and not e['whole_image_identity']
 print('Time sync control flow authenticated:8192 cases;224 supplemental native bytes;62 imports;callback/query/recovery/private-frame/image gates retained')
if __name__=='__main__':audit()
