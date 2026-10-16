#!/usr/bin/env python3
"""Authenticate role control and keep exact fatal transfer explicitly unresolved."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-phone-role'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-phone-role-runtime/report.json';b=read(rp)
 assert r['comparisons']==4800 and r['fatal_boundary_cases']==472 and r['observations_per_side']==36558 and r['trace_sha256']=='4fa8b4acf141e835716cb3860b63d5a8e96fcfb3e048deb6a862baf2e202064b'
 for flag in ['source_log_texts_match','fresh_connection_fields_and_modes_checked','full_word_handle_and_low_halfword_store_checked','raw_r0_callee_sp_checked_on_returning_paths','terminal_paths_stop_before_native_stack_blx','no_trap_or_executable_array_substitution','only_logging_delay_status_publish_and_terminal_boundary_are_fixtures','observed_nonstack_ram_checked','no_native_candidate_execution']:assert r[flag]
 for flag in ['fatal_transfer_implemented','whole_role_status_or_logging_graph_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_phone_role.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['role_object_sha256']==sha(rp.parent/'phone-role-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_phone_role_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['helper_object_sha256']==sha(rp.parent/'role-fields-source.o') and b['linked_sha256']==sha(rp.parent/'native-phone-role-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==71 and undefined_symbols(rp.parent/'native-phone-role-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'phone-role-source.o')[0]==b['role_undefined_symbols'] and len(b['role_undefined_symbols'])==9
 parent=read(BASE/'native-ble-message-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_phone_connection_role_assign'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']==['r1_phone_role_assertion_stack_transfer']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in e['byte_read_sizes'].items():
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 q=read(OUT/'rea-4da28.json')['structuredContent'];assert q['normalized_result']['body']['total_bytes']==430 and 'terminal call' in str(q['limitations'])
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==1 and e['new_ownership_rows'][0] in rows and int(e['new_ownership_rows'][0]['size'])==430
 from audit_source_frontier import section_bytes
 obj=OUT/'native_phone_role.o';total=0
 for i,a in enumerate(e['text_addresses']):
  n=e['byte_read_sizes'][f'{a:x}'];total+=n;assert section_bytes(obj,f'.r1.phone.role.text{i}',executable=False)==raw[a-0x27000:a-0x27000+n]
 assert total==e['new_owned_text_bytes']==667 and e['connection_fields_reused_not_new'] and e['supplemental_veneer_not_new_row']
 gate=e['fatal_transfer_gate'];assert gate['native_store_word']=='0xe7f00000' and gate['source_unresolved_provider'] in b['undefined_symbols'] and gate['native_even_stack_target'] and not gate['implemented'] and not gate['substitute_trap_or_opcode_array'] and not e['whole_image_identity']
 print('Phone role authenticated:4800 cases incl472 fatal boundaries;430 native bytes;667 text bytes;71 imports;exact fatal transfer, full ABI and image gates open')
if __name__=='__main__':audit()
