#!/usr/bin/env python3
"""Authenticate health state publication and sleep service wrapper contracts."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-service-wrappers';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_health_service_wrappers.py')==c['generator_sha256']
 parent=BASE/'native-health-daily-logging';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-health-daily-logging-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-health-service-wrappers-runtime.o','linked_sha256','undefined_symbols'),('wrappers-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==72 and b['closed_parent_imports']==['r1_event_service_0008e154','r1_event_service_0008e1e0','r1_event_service_0008e274','r1_event_service_0008e552','r1_event_service_0008e55c'] and b['newly_exposed_imports']==['r1_sleep_sync_status_backend'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['new_ram_state_bytes']==0
 sections=allocated_sections(OUT/'native_health_service_wrappers.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(OUT/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(rr['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==208 and c['native_span_bytes']==b['native_source_span_bytes']==354 and c['service_wrappers_and_publish_helpers_execute']
 for x in c['bodies'][:2]:assert [d['value'] for d in x['data'] if d['kind']=='word']==['__start_log_const_data+224','__start_log_const_data']
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_service_wrappers.py')==v['driver_sha256'] and v['comparisons']==18656 and v['counts']=={'status':8580,'sync':528,'spo2':4608,'temperature':4608,'bridge_spo2':36,'bridge_temperature':36,'noop':260,'mode_calls':44856,'printf':12816,'std':11214,'publish':288,'backend':594} and v['trace_sha256']=='7c638de739a2c0d1d8e701e01f5777391200bc587a4d4e09ac15ba745c751471'
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==7 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==354 and v['independent_guard_log_return_and_stack_payload_oracle'] and v['bridges_execute_actual_publish_helpers'] and v['log_mode_publish_and_sleep_backend_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Health wrappers:18656 comparisons;354 exact verification bytes;five imports close/one backend exposed;72 remain;provider/layout/image gates open')
if __name__=='__main__':audit()
