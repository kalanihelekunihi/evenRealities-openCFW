#!/usr/bin/env python3
"""Authenticate profile event construction while retaining external tail/history gates."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-user-profile-command'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-user-profile-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==76384 and r['counts']==dict(matrix=50176,fields=18144,workflow=8064) and r['observations_per_side']==417004 and r['trace_sha256']=='a546fe2f18de7337489d6e66af7e0a153c99086e71402580c76fb5c0d8ab0d8a' and all(r['lower_observation_counts'].values())
 for flag in ['actual_packet_accessor_and_flag_ack','only_lower_response_event_logging_are_fixtures','all_first_byte_values_and_halfword_edges_checked','event_last_two_bytes_preserve_seed_and_mutations','two_call_event_tail_workflows_checked','fresh_payload_after_logs_and_ack_checked','raw_r0_callee_sp_and_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['portable_policy_modified','runtime_admission_changed','hardware_write_executed','profile_event_delivery_proven','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_user_profile.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'user-profile-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_user_profile_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-user-profile-runtime.o') and b['accessor_object_sha256']==sha(rp.parent/'profile-accessor-source.o') and b['ack_object_sha256']==sha(rp.parent/'profile-flag-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==53 and undefined_symbols(rp.parent/'native-user-profile-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'user-profile-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'profile-accessor-source.o')[0]==[] and undefined_symbols(rp.parent/'profile-flag-source.o')[0]==['r1_protocol_send_response']
 parent=read(BASE/'native-health-settings-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_user_profile_handler'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n,suffix in [('84a10',202,''),('84adc',31,''),('84b00',8,''),('84b08',25,''),('84adc',34,'-full'),('84b08',28,'-full')]:
  q=read(OUT/f'rea-bytes-{a}{suffix}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 assert 'No procedure exists' in str(read(OUT/'rea-procedure.json')) and e['procedure_metadata_missing']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==202
 from audit_source_frontier import section_bytes
 for section,a,n in [('ring',0x84adc,34),('sdk',0x84b08,28)]:assert section_bytes(OUT/'native_user_profile_command.o','.r1.profile.command.'+section,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['native_code_bytes']==202 and e['new_owned_text_bytes']==62 and e['separate_native_handler'] and e['event_initializes10_publishes12'] and e['external_event_tail_no_defaults'] and not e['portable_policy_modified'] and not e['runtime_admission_changed'] and not e['whole_image_identity']
 print('Native profile command:76384 cases;202 native+62 text bytes;actual accessor/ack;53 imports;two raw tail bytes and caller/history/event/image gates retained')
if __name__=='__main__':audit()
