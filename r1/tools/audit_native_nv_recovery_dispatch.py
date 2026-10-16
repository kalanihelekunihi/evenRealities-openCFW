#!/usr/bin/env python3
"""Authenticate build-only dispatcher with unresolved merge/report effect boundaries."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nv-recovery-dispatch'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-nv-recovery-dispatch-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==6496 and r['counts']==dict(envelope=3472,query=84,dispatch=2940) and r['observations_per_side']==22696 and r['trace_sha256']=='4e63b8da6a93654122519b7344b50be32b17b544d634cfa99cf53bbfc4e318ba'
 for flag in ['actual_accessor_phone_getter_inverse_header','actual_native_dispatch','only_merge_report_response_and_logging_are_fixtures','unused_lower_boundary_scratch_registers_not_compared','post_accessor_mutations_are_explicit_fixtures','short_backing_reads_only_in_mapped_emulator_fixture','fresh_envelope_fields_after_logs_checked','query_r0_r1_r2_r3_and_callee_sp_checked','raw_r0_and_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['bounded_planner_modified','hardware_write_executed','merge_and_identity_report_effects_implemented','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_nv_recovery_dispatch.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'nv-recovery-dispatch-graph-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_nv_recovery_dispatch_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-nv-recovery-dispatch-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==61 and undefined_symbols(rp.parent/'native-nv-recovery-dispatch-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'nv-recovery-dispatch-graph-source.o')[0]==b['graph_undefined_symbols'] and len(b['graph_undefined_symbols'])==8
 parent=read(BASE/'native-nv-recovery-envelope-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_native_nv_recovery_command_dispatch'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==[e['merge_boundary'],e['report_boundary']]
 assert not b['bounded_planner_modified'] and not b['merge_and_identity_report_effects_implemented'] and not b['hardware_write_executed']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('7c450',108),('7c4bc',54),('7c4f4',8),('7c4fc',48),('7bd68',40),('7bbe8',10)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 assert 'No procedure exists' in str(read(OUT/'rea-7c450.json')) and e['rea_procedure_gap']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==108
 from audit_source_frontier import section_bytes
 for name,a,n in [('ring',0x7c4bc,54),('sdk',0x7c4fc,48)]:assert section_bytes(OUT/'native_nv_recovery_dispatch.o','.r1.nv.dispatch.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['build_only_control_flow'] and not e['incoming_lower_scratch_abi_verified'] and not e['planner_or_runtime_admission_changed'] and not e['identity_table_copied'] and e['new_owned_text_bytes']==102 and not e['whole_image_identity']
 print('Build-only recovery dispatch authenticated:6496 graph/direct cases;108 native+102 text bytes;61 imports;merge/report/admission/frame/ABI/image gates retained')
if __name__=='__main__':audit()
