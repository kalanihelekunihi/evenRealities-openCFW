#!/usr/bin/env python3
"""Authenticate ACK contracts, owned mutex configuration and shared workspace reuse."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-ack';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-protocol-ack-runtime/report.json';b=read(rp);raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
 assert r['workflows']==10160 and r['counts']=={'lock':96,'unlock':96,'payload':40,'resolve':3796,'packet':5940,'restart':96,'noop':96} and r['observations_per_side']==47312 and r['trace_sha256']=='212cf2da9fdba992d94b9bdaa3fddfac3c8a0533a80ef9657aec5ac5a59bc262'
 for flag in ['actual_source_accessor_lock_unlock_resolver_handler','all32_slots_duplicate_first_match_and_two_call_sequences','full_word_keys_not_truncated_by_resolver','lazy_mutex_null_creation_and_unconditional_acquire_checked','clear_before_unlock_callback_captured_before_unlock','mutex_and_delayed_and_ack_callback_bodies_are_fixtures','source_workspace_reused','source_descriptor_and_name_match_native','source_restart_callback_two_bytes_match_native','controlled_provider_mutations_not_physical_concurrency','raw_r0_callee_sp_and_observed_nonstack_ram_checked','candidate_native_execution_forbidden_except_compiled_noop']:assert r[flag]
 assert not r['whole_ack_rtos_graph_executed'] and not r['physical_concurrency_verified'] and not r['full_raw_abi_verified'] and not r['instruction_identity'] and not r['whole_image_complete']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_ack.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['ack_object_sha256']==sha(rp.parent/'protocol-ack-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_protocol_ack_verification.ld') and r['application_sha256']==hashlib.sha256(raw).hexdigest()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['workspace_object_sha256']==sha(rp.parent/'workspace-source.o') and b['linked_sha256']==sha(rp.parent/'native-protocol-ack-runtime.o') and len(b['undefined_symbols'])==76
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(rp.parent/'protocol-ack-source.o')[0]==b['ack_undefined_symbols']==['osMutexAcquire','osMutexNew','osMutexRelease','r1_native_delayed_cancel','r1_native_delayed_schedule'] and undefined_symbols(rp.parent/'native-protocol-ack-runtime.o')[0]==b['undefined_symbols']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 for p in OUT.glob('ghidra-*.json'):
  g=read(p);a=int(g['address'],16);assert bytes(g['data'])==raw[a-0x27000:a-0x27000+g['length']]
 sizes={0x48234:28,0x48258:14,0x82bd4:18,0x83028:124}
 for p in OUT.glob('rea-*.json'):
  q=read(p);q=q.get('structuredContent') or json.loads(next(x['text'] for x in q['content'] if x['type']=='text'));a=int(p.stem.split('-')[1],16)
  if a in sizes:assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==sizes[a]
  else:assert 'No procedure exists' in str(q)
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['ownership_rows'])==6 and all(row in rows for row in e['ownership_rows']) and sum(int(x['size']) for x in e['ownership_rows'])==242 and not e['supplemental_restart_callback_has_locked_row']
 from audit_source_frontier import section_bytes
 obj=OUT/'native_protocol_ack.o';cold=ROOT/e['cold_observation'];assert section_bytes(obj,'.r1.ack.mutex',executable=False)==cold.read_bytes()[0x6e4:0x6e8]==bytes(4)
 assert section_bytes(obj,'.r1.ack.mutex.control',executable=False)==bytes(80) and 0x20007e04<=0x20019ea4<0x20019ea4+80<=0x20007e04+0x340b4
 assert section_bytes(obj,'.r1.ack.mutex.name',executable=False)==b'ack_mutex\0' and section_bytes(obj,'.r1.ack.restart.callback')==raw[0x4d2f0-0x27000:0x4d2f2-0x27000] and section_bytes(rp.parent/'workspace-source.o','.r1.protocol.reset.workspace',executable=False)==bytes(640)
 print('ACK source authenticated:10160 workflows;6 rows242 bytes +supplemental2-byte callback;76 imports;actual RTOS/concurrency/private ABI/image gates open')
if __name__=='__main__':audit()
