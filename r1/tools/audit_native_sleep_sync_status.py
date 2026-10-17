#!/usr/bin/env python3
"""Authenticate sleep sync backend, bounded context prefix and wrapper tests."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sync-status';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256s'][str(Path(u['command'][-1]).relative_to(ROOT))]
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_sleep_sync_status.py')==c['generator_sha256']
 parent=BASE/'native-health-service-wrappers';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-health-service-wrappers-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-sleep-sync-status-runtime.o','linked_sha256','undefined_symbols'),('sync-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==71 and b['closed_parent_imports']==['r1_sleep_sync_status_backend'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['new_ram_state_bytes']==12
 x=c['bodies'][0];assert sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==228 and x['source_span_bytes']==c['native_span_bytes']==b['native_source_span_bytes']==412 and sha(OUT/'disassembly-5b6f4.txt')==x['disassembly_sha256']
 sections=allocated_sections(OUT/'native_sleep_sync_status.o');assert sections['.text.r1_sleep_sync_status_backend'][2]==412 and sections['.r1.sleep.sync.context'][2]==12
 r=json.loads((OUT/'rea-5b6f4.json').read_text())['structuredContent'];rr=r['normalized_result'];a=0x5b6f4-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==412 and bytes.fromhex(rr['bytes_hex'])==raw[a:a+412]
 initialized=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(initialized)==c['initialized_data_sha256']=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and initialized.read_bytes()[0x30c:0x318]==bytes(12) and c['context_prefix_address']=='0x200067b4' and not c['full_context_extent_owned'] and c['io_callbacks_unresolved']
 assert [d['value'] for d in x['data'] if d['kind']=='word']==['__start_log_const_data+224','__start_log_const_data','0x11223344','r1_sleep_sync_context_prefix']
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_sleep_sync_status.py')==v['driver_sha256'] and v['comparisons']==34912 and v['counts']=={'direct':17456,'wrapper':17456,'reads':118080,'writes':25120,'clears':58176,'printf':21296,'std':15120} and v['trace_sha256']=='300655f9c54196fef1b1084368d4eea45117803311c55f8339d3dd9405b7f240'
 for p,h in v['object_sha256s'].items():assert sha(ROOT/p)==h
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==8 and sum(x['size'] for x in v['exact_spans'])==v['exact_joint_bytes']==766 and v['exact_new_bytes']==412 and v['independent_record_partial_read_and_write_marker_oracle'] and v['actual_wrapper_and_backend_execute'] and v['io_memclear_and_log_providers_are_fixtures'] and not v['full_context_extent_owned'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Sleep sync backend/context compile;766 joint exact bytes;71 imports;I/O/context/private/layout/image gates open')
if __name__=='__main__':audit()
