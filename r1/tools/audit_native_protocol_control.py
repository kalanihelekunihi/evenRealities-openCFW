#!/usr/bin/env python3
"""Bind protocol control source, REA byte evidence and behavioral receipts."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-control'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-protocol-control-runtime/report.json';b=read(rp)
 assert r['comparisons']==8344 and r['counts']==dict(connection=2304,pair=3840,report=512,command=216,signal=192,setting=1280) and r['observations_per_side']==18842 and r['trace_sha256']=='7a2cde9279bf185e3f8928861af2755071ddfb8f65660983ea8d25a679a7ff9d'
 for flag in ['actual_source_payload_flag_checked_phone_helpers','actual_setting_plan_to_report_setter','post_accessor_length_mutations_are_explicit_fixtures','fresh_mode_payload_sequence_phone_and_thread_reads_checked','provider_failures_do_not_add_early_aborts','report_full_word_log_then_low_byte_store_checked','only_logging_transport_role_os_are_fixtures','source_log_texts_match','raw_r0_callee_sp_and_observed_nonstack_ram_checked','private_response_pointer_not_compared','no_native_candidate_execution']:assert r[flag]
 for flag in ['whole_dispatch_or_rtos_graph_executed','physical_pairing_adv_or_reset_verified','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_control.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['control_object_sha256']==sha(rp.parent/'protocol-control-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_protocol_control_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['helper_object_sha256']==sha(rp.parent/'control-helpers-source.o') and b['linked_sha256']==sha(rp.parent/'native-protocol-control-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==72 and undefined_symbols(rp.parent/'native-protocol-control-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'protocol-control-source.o')[0]==b['control_undefined_symbols'] and len(b['control_undefined_symbols'])==8
 parent=read(BASE/'native-protocol-serial-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports'] and sorted(set(b['undefined_symbols'])-set(parent))==b['newly_exposed_imports']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in e['byte_read_sizes'].items():
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==3 and all(x in rows for x in e['new_ownership_rows']) and sum(int(x['size']) for x in e['new_ownership_rows'])==284 and e['supplemental_native_bytes']==52
 from audit_source_frontier import section_bytes
 obj=OUT/'native_protocol_control.o'
 for name,a,n in [('report_ring',0x8b87c,49),('report_sdk',0x8b8b8,43),('pair_ring',0x8436c,43),('pair_sdk',0x843a0,37)]:assert section_bytes(obj,'.r1.control.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 cold=(BASE/'native-scatter-data/observed-initialized-data.bin').read_bytes()
 for name,a,n in [('report.enabled',0x200067a0,1),('service.thread',0x20006570,4)]:assert section_bytes(obj,'.r1.control.'+name,executable=False)==cold[a-0x200064a8:a-0x200064a8+n]==bytes(n)
 for folder in ['initial-field6-harness','initial-no-target-read-attempt']:
  history=OUT/folder
  for p,h in read(history/'manifest.json')['files'].items():assert sha(history/p)==h,p
 assert not e['direct_ghidra_mcp_available'] and e['rea_headless_ghidra_bytes_authenticated'] and not e['whole_image_identity']
 print('Protocol control authenticated:8344 comparisons;3 new rows/284 bytes +52 supplemental;177 owned data bytes;72 imports;image and physical gates open')
if __name__=='__main__':audit()
