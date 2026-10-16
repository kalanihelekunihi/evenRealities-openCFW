#!/usr/bin/env python3
"""Authenticate system command graph with explicit supplemental and context gates."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-system-event-commands'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=BASE/'native-system-event-runtime/report.json';b=read(rp);r=read(rp.parent/'verification.json');e=read(OUT/'evidence.json')
 assert r['comparisons']==7560 and r['counts']==dict(event=1512,ack=1512,query=1512,mode=1512,op3=1512) and r['observations_per_side']==28505 and r['trace_sha256']=='0cd7eb9c5f49731ebef8a657eb29838987191fd80228c3c0a905d8ab4ad18831'
 for flag in ['actual_commands_mode_op3_response_encoder_gates_crc_memory_hook','post_getter_and_accessor_mutations_are_explicit_fixtures','only_allocator_logging_event_and_lower_callback_are_fixtures','raw_r0_callee_sp_and_observed_nonstack_ram_checked','private_header_pointer_not_compared','no_native_candidate_execution']:assert r[flag]
 for flag in ['whole_event_allocator_ble_or_rtos_graph_executed','full_raw_abi_verified','instruction_identity','whole_image_complete']:assert not r[flag]
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_system_event.py') and r['report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(rp.parent/'system-event-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_system_event_verification.ld')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 for p,h in b['helpers'].items():assert sha(rp.parent/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-system-event-runtime.o')
 from build_source_candidates import undefined_symbols
 assert len(b['undefined_symbols'])==62 and undefined_symbols(rp.parent/'native-system-event-runtime.o')[0]==b['undefined_symbols'] and undefined_symbols(rp.parent/'system-event-source.o')[0]==b['graph_undefined_symbols'] and len(b['graph_undefined_symbols'])==8
 parent=read(BASE/'native-response-graph-runtime/report.json')['undefined_symbols'];assert sorted(set(parent)-set(b['undefined_symbols']))==b['closed_parent_imports']==['r1_protocol_command_000844ec','r1_protocol_command_00084860','r1_protocol_command_00084b24'] and not b['newly_exposed_imports']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['tool_receipts','supplemental_evidence']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes();assert hashlib.sha256(raw).hexdigest()==r['application_sha256']
 for a,n in [('844ec',54),('84860',20),('84b24',120),('4c5b8',8),('4c5c0',4),('83c62',36),('84b9c',53),('84bdc',47),('84bd4',8)]:
  q=read(OUT/f'rea-bytes-{a}.json')['structuredContent'];d=q['normalized_result'];i=int(a,16)-0x27000
  assert q['provider']['id']=='ghidra' and q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and d['complete'] and d['returned_bytes']==d['requested_bytes']==n and bytes.fromhex(d['bytes_hex'])==raw[i:i+n]
 for a in e['rea_procedure_gaps']:assert 'No procedure exists' in str(read(OUT/f'rea-{a}.json'))
 q=read(OUT/'rea-4c5b8.json')['structuredContent'];assert q['normalized_result']['body']['total_bytes']==8
 assert int.from_bytes(raw[0x4c5c0-0x27000:0x4c5c4-0x27000],'little')+36==0x2001e478
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==2 and all(x in rows for x in e['new_ownership_rows']) and sum(int(x['size']) for x in e['new_ownership_rows'])==44 and sum(e['supplemental_body_ranges'].values())==194
 assert not any(x['entry'] in ['0x000844ec','0x00084860','0x00084b24'] for x in rows)
 from audit_source_frontier import section_bytes
 obj=OUT/'native_system_event_commands.o';assert section_bytes(obj,'.r1.system.command.health_mode',executable=False)==bytes(1) and 0x20007e04<=0x2001e478<0x20007e04+0x340b4
 for name,a,n in [('wear_ring',0x84b9c,53),('wear_sdk',0x84bdc,47)]:assert section_bytes(obj,'.r1.system.command.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert e['new_owned_data_bytes']==101 and e['supplemental_bytes_not_rows']==194 and not e['whole_image_identity']
 print('System commands authenticated:7560 cases;2 locked rows/44 bytes+194 supplemental;101 owned bytes;62 imports;metadata/context/ABI/image gates open')
if __name__=='__main__':audit()
