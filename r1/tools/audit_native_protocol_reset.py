#!/usr/bin/env python3
"""Authenticate protocol reset with explicit supplemental callback and fixture limits."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-reset';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-protocol-reset-runtime/report.json';b=read(rp);raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
 assert r['comparisons']==4608 and r['counts']=={'reset':1536,'arm':1536,'tick':1536} and r['events_per_side']==9216 and r['trace_sha256']=='a933a678935e97e22e71c124bbd40786c6881d33cb5b00c4d775f1c292e51936'
 for flag in ['actual_source_clear','init_scheduler_and_event_are_named_fixtures','one_byte_event_payload_checked_private_pointer_not_compared','source_callback_placed_at_native_address_for_pointer_equality','callback_native_body_execution_replaced_with_compiled_source','raw_r0_callee_sp_and_observed_nonstack_ram_checked']:assert r[flag]
 assert not r['whole_protocol_graph'] and not r['instruction_identity'] and not r['whole_image_complete'] and r['source_callback_bytes']==64
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_reset.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['reset_object_sha256']==sha(rp.parent/'protocol-reset-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_protocol_reset_verification.ld') and r['application_sha256']==hashlib.sha256(raw).hexdigest()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 for p,h in b['selected_objects'].items():assert sha(rp.parent/p)==h,p
 assert b['linked_sha256']==sha(rp.parent/'native-protocol-reset-runtime.o') and b['reset_undefined_symbols']==['r1_event_publish','r1_native_delayed_schedule','r1_proto_port_init'] and len(b['undefined_symbols'])==54 and 'r1_native_proto_port_reset' not in b['undefined_symbols'] and 'r1_proto_port_init' in b['undefined_symbols']
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(rp.parent/'protocol-reset-source.o')[0]==b['reset_undefined_symbols'] and undefined_symbols(rp.parent/'native-protocol-reset-runtime.o')[0]==b['undefined_symbols']
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 for p in OUT.glob('ghidra-*.json'):
  g=read(p);a=int(g['address'],16);assert bytes(g['data'])==raw[a-0x27000:a-0x27000+g['length']]
 for p in OUT.glob('rea-*.json'):assert 'No procedure exists' in str(read(p))
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_rows']==[x for x in rows if x['image']=='application' and x['entry'] in ['0x00082f78','0x00083cf4']]
 assert e['locked_native_bytes']==40 and e['supplemental_callback_native_bytes']==30 and not e['supplemental_callback_has_locked_row'] and not e['whole_image_identity']
 from audit_source_frontier import section_bytes
 assert section_bytes(OUT/'native_protocol_reset.o','.r1.protocol.reset.workspace',executable=False)==bytes(640) and 0x20007e04<=0x20019ef4<0x20019ef4+640<=0x20007e04+0x340b4
 assert section_bytes(rp.parent/'sequence-source.o','.r1.protocol.sequence',executable=False)==section_bytes(BASE/'native-protocol-encoder/native_protocol_encoder.o','.r1.protocol.sequence',executable=False)
 print('Protocol reset authenticated:4608 cases;2 locked rows plus supplemental callback;54 imports with port-init newly exposed;placement/private ABI/graph gates open')
if __name__=='__main__':audit()
