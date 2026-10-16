#!/usr/bin/env python3
"""Bind build-only native recovery envelope while retaining admission/dispatch gates."""
import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-nv-recovery-envelope'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-nv-recovery-envelope-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==3556 and r['counts']==dict(envelope=3472,query=84) and r['observations_per_side']==15722 and r['trace_sha256']=='64778eddec35512bcf0bd554ebc76a5ee15dd03f251878d795e9bfbcb1a4af29'
 for flag in ['actual_accessor_phone_getter_inverse_header','lower_native_dispatch_is_fixture_only','post_accessor_mutations_are_explicit_fixtures','short_backing_reads_only_in_mapped_emulator_fixture','fresh_envelope_fields_after_logs_checked','query_r0_r1_r2_r3_and_callee_sp_checked','raw_r0_and_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['bounded_planner_modified','hardware_write_executed','native_persistent_dispatch_implemented','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_nv_recovery_envelope.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['envelope_object_sha256']==sha(rp.parent/'nv-recovery-envelope-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_nv_recovery_envelope_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['owner_object_sha256']==sha(rp.parent/'envelope-existing-helpers-source.o') and b['header_object_sha256']==sha(rp.parent/'inverse-header-source.o') and b['linked_sha256']==sha(rp.parent/'native-nv-recovery-envelope-runtime.o')
 from build_source_candidates import undefined_symbols
 linked=rp.parent/'native-nv-recovery-envelope-runtime.o';assert len(b['undefined_symbols'])==60 and undefined_symbols(linked)[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'nv-recovery-envelope-source.o')[0]==b['envelope_undefined_symbols'] and len(b['envelope_undefined_symbols'])==6
 parent=read(BASE/'native-nv-class-writer-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_nv_recovery_command_handler_plan_decode'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_native_nv_recovery_command_dispatch']
 assert not b['bounded_planner_modified'] and not b['persistent_dispatch_supplied'] and not b['hardware_write_executed']
 syms={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(linked)],text=True).splitlines() if len(v:=line.split())==3};assert b['native_envelope_alias']==[e['legacy_build_alias'],e['native_name']] and syms[e['legacy_build_alias']]==syms[e['native_name']] and e['persistent_dispatch_unresolved'] in b['undefined_symbols']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('84150',176),('84200',8),('84208',47),('84238',41),('84264',54),('8429c',48),('83c86',32)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for a in e['rea_procedure_gaps']:assert 'No procedure exists' in str(read(OUT/f'rea-{a}.json'))
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==2 and all(x in rows for x in e['new_ownership_rows']) and sum(int(x['size']) for x in e['new_ownership_rows'])==208
 from audit_source_frontier import section_bytes
 for name,a,n in [('null_ring',0x84208,47),('null_sdk',0x84238,41),('fields_ring',0x84264,54),('fields_sdk',0x8429c,48)]:assert section_bytes(OUT/'native_nv_recovery_envelope.o','.r1.nv.envelope.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['build_only_native_boundary'] and not e['planner_or_runtime_admission_changed'] and not e['identity_table_copied'] and e['new_owned_text_bytes']==190 and not e['whole_image_identity']
 print('Build-only recovery envelope authenticated:3556 cases;2 rows/208 bytes+190 text;60 imports;native dispatch/admission/identity/frame/ABI/image gates retained')
if __name__=='__main__':audit()
