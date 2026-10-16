#!/usr/bin/env python3
"""Authenticate supplemental power-control command and retained native frame."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-power-command'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-power-command-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==39168 and r['counts']==dict(null=2304,rejected=9108,changed=13848,reset=4636,off=4636,resume=4636) and r['observations_per_side']==113876 and r['trace_sha256']=='98c393d29a8a0db6338c386d04dafa71bb994fc0c59977d802875f4a9d4a2ef4'
 for flag in ['actual_packet_accessor','all_lower_effects_are_fixtures','explicit_post_call_mutations','command_reread_after_delay_checked','event_preserves_incoming_upper16','tail_and_nontail_r2_r3_restore_checked','raw_r0_r2_r3_callee_sp_and_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['runtime_admission_changed','hardware_write_executed','full_raw_abi_verified','cross_call_private_frame_history_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_power_command.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'power-command-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_power_command_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-power-command-runtime.o') and b['helper_object_sha256']==sha(rp.parent/'power-command-helpers-source.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==59 and undefined_symbols(rp.parent/'native-power-command-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'power-command-source.o')[0]==b['graph_undefined_symbols'] and undefined_symbols(rp.parent/'power-command-helpers-source.o')[0]==[]
 parent=read(BASE/'native-time-sync-providers-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_protocol_command_000843c8'] and b['newly_exposed_imports']==[] and not(set(b['undefined_symbols'])-set(parent))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n,suffix in [('843c8',210,''),('8449c',20,''),('c0278',71,''),('c02c4',65,''),('c0278',75,'-full'),('c02c4',69,'-full')]:
  q=read(OUT/f'rea-bytes-{a}{suffix}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 assert 'No procedure exists' in str(read(OUT/'rea-procedure.json')) and e['missing_ghidra_procedure_metadata']
 from audit_source_frontier import section_bytes
 for name,a,n in [('ring',0xc0278,75),('sdk',0xc02c4,69)]:assert section_bytes(OUT/'native_power_command.o','.r1.power.command.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['native_code_bytes']==210 and e['new_ownership_rows']==[] and e['new_owned_text_bytes']==144 and e['tail_flags_restore_before_call'] and e['event_flags_restore_after_call'] and e['seed_upper16_preserved'] and not e['runtime_admission_changed'] and not e['private_frame_history_verified'] and not e['whole_image_identity']
 print('Power control command authenticated:39168 cases;210 supplemental native+144 text bytes;59 imports;actual accessor;raw/private/effect/image gates retained')
if __name__=='__main__':audit()
