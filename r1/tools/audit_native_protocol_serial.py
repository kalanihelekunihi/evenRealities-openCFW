#!/usr/bin/env python3
"""Authenticate serial/header source, owned cold class and explicit private-history boundary."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-serial';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');e=read(OUT/'evidence.json');rp=BASE/'native-protocol-serial-runtime/report.json';b=read(rp);raw=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()
 assert r['comparisons']==18744 and r['counts']=={'ack':2048,'inverse':2048,'checked':2048,'read':10800,'serial':1800} and r['observations_per_side']==32272 and r['trace_sha256']=='590e87fed694e6b0cc945abf50cd11e27ad69a6ccccbce2ec3c0d2d27d46dc54'
 for flag in ['actual_source_memory_move_and_fill','source_cold_class148_and_symbolic_handle4_match','actual_source_header_and_checked_helpers','header_checked_r0_through_r3_with_lower_register_clobbers_checked','raw_record_and_serial_output_pointer_identity_checked','failed_partial_reads_preserve_external_raw_record','only_kv_read_and_lower_response_are_fixtures','raw_r0_callee_sp_and_observed_nonstack_ram_checked','private_header_pointers_not_compared','candidate_native_execution_forbidden']:assert r[flag]
 assert not r['whole_kv_transport_graph_executed'] and not r['physical_serial_or_delivery_verified'] and not r['full_raw_abi_verified'] and not r['instruction_identity'] and not r['whole_image_complete']
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_serial.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['serial_object_sha256']==sha(rp.parent/'protocol-serial-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_protocol_serial_verification.ld') and r['application_sha256']==hashlib.sha256(raw).hexdigest()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 assert b['memory_object_sha256']==sha(rp.parent/'serial-memory-source.o') and b['linked_sha256']==sha(rp.parent/'native-protocol-serial-runtime.o') and len(b['undefined_symbols'])==74
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(rp.parent/'protocol-serial-source.o')[0]==b['serial_undefined_symbols']==['r1_kv_class_read','r1_protocol_send_response'] and undefined_symbols(rp.parent/'native-protocol-serial-runtime.o')[0]==b['undefined_symbols']
 for p,h in e['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in e['tool_receipts'].items():assert sha(OUT/p)==h,p
 for p in OUT.glob('ghidra-*.json'):
  g=read(p);a=int(g['address'],16);assert bytes(g['data'])==raw[a-0x27000:a-0x27000+g['length']]
 sizes={0x7ba78:70,0x82b54:66,0x82b96:62,0x84c5e:36}
 for p in OUT.glob('rea-*.json'):
  q=read(p);q=q.get('structuredContent') or json.loads(next(x['text'] for x in q['content'] if x['type']=='text'));a=int(p.stem.split('-')[1],16)
  if a in sizes:assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['body']['total_bytes']==sizes[a]
  else:assert 'No procedure exists' in str(q)
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert len(e['new_ownership_rows'])==4 and all(row in rows for row in e['new_ownership_rows']) and sum(int(x['size']) for x in e['new_ownership_rows'] if x['size'])==164
 assert not e['single_canonical_getter_selected'] and not e['private_stack_history_matches'] and not e['whole_image_identity']
 assert next(x for x in e['new_ownership_rows'] if x['entry']=='0x00083db0')['size']=='' and e['observed_serial_instruction_span_bytes']==52 and e['existing_getter_not_new_row']['entry']=='0x0007ba78' and e['existing_getter_not_new_row'] in rows
 from audit_source_frontier import section_bytes
 obj=OUT/'native_protocol_serial.o';cold=ROOT/e['cold_observation'];assert section_bytes(obj,'.r1.serial.kv.class',executable=False)==cold.read_bytes()[0x630:0x630+148] and cold.read_bytes()[0x1954:0x1958]==bytes.fromhex('d86a0020')
 rel=subprocess.check_output(['arm-none-eabi-readelf','-r',str(obj)],text=True);block=rel.split("Relocation section '.rel.r1.serial.kv.handle'",1)[1].split('Relocation section',1)[0];assert 'contains 1 entry' in block and 'R_ARM_ABS32' in block and 'r1_serial_record_class' in block
 h=read(OUT/'history-probe.json');assert h['driver_sha256']==r['driver_sha256'] and h['runtime_report_sha256']==sha(rp) and h['object_sha256']==r['object_sha256'] and not h['private_stack_history_matches_all'] and len(h['probes'])==4
 for q in h['probes']:
  assert q['first_match'] and not q['second_match'];n,s=q['steps'][1];assert n[0]==s[0] and n[2]==s[2] and [x for x in n[1] if x[0]=='response']==[x for x in s[1] if x[0]=='response']
  a=next(x for x in n[1] if x[0]=='kv');c=next(x for x in s[1] if x[0]=='kv');diff=[i for i,(x,y) in enumerate(zip(bytes.fromhex(a[3]),bytes.fromhex(c[3]))) if x!=y];assert diff and min(diff)>=72 and max(diff)<=123
 for folder in ['initial-c-header-candidate','register-bridge-candidate','pre-class-initializer-candidate']:
  history=OUT/folder;m=read(history/'manifest.json')
  for p,digest in m['files'].items():assert sha(history/p)==digest,p
 cr=rp.parent/'cold-graph-report.json';cb=read(cr);g=read(rp.parent/'cold-graph-verification.json');assert g['workflows']==432 and g['cached_reads_per_side']==432 and g['critical_callbacks_per_side']==216 and g['trace_sha256']=='43b6ecaa0e3db6e6b11d6d70f8fa91653fb3830a7390ba1f3f920a44a32bf33d'
 assert g['actual_source_kv_class_memory_getter_headers_and_handler'] and g['only_critical_callbacks_and_lower_response_are_fixtures'] and g['cold_source_class_and_symbolic_handle_match'] and not g['whole_flash_or_transport_graph_executed'] and not g['private_stack_history_verified'] and not g['whole_image_complete']
 assert g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_serial_cold_graph.py') and g['report_sha256']==sha(cr) and g['object_sha256']==cb['graph_object_sha256']==sha(rp.parent/'serial-cold-class-graph-source.o') and g['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_protocol_serial_cold_graph_verification.ld') and g['application_sha256']==r['application_sha256']
 for p,digest in cb['inputs'].items():assert sha(ROOT/p)==digest,p
 for group in ['provider_reports','objects']:
  for p,digest in cb[group].items():assert sha(BASE/p)==digest,p
 assert cb['selected_object_sha256']==sha(rp.parent/'kv-class-read-source.o') and cb['undefined_symbols']==['r1_kv_port','r1_protocol_send_response'] and undefined_symbols(rp.parent/'serial-cold-class-graph-source.o')[0]==cb['undefined_symbols']
 print('Serial source authenticated:18744 cases +432 cached-class workflows;4 new rows with manual52-byte observed span;74 imports;private history72-123/canonical getter/image gates open')
if __name__=='__main__':audit()
