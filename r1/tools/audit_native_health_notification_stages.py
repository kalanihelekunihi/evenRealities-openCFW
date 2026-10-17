#!/usr/bin/env python3
"""Authenticate sync-controller source, native span identity and remaining callback gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-health-notification-stages';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==r['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for x in b['units']:assert x['compiled'] and sha(ROOT/x['source'])==x['source_sha256'] and sha(Path(x['command'][-1]))==x['object_sha256']
 parent=BASE/'native-health-notification-throttle';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-health-notification-throttle-runtime.o')==b['parent_object_sha256']
 assert sha(out/'native-health-notification-stages-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-health-notification-stages-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==90 and len(b['closed_parent_imports'])==5 and len(b['newly_exposed_imports'])==34
 assert sha(out/'stages-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'stages-source.o')[0]==b['graph_undefined_symbols']
 assert sha(out/'contracts.json')==b['contracts_sha256'] and sha(out/'text-spans.json')==b['text_spans_sha256'] and sum(x['size'] for x in c['bodies'])==b['native_body_bytes']==3400 and len(c['providers'])==47 and c['source_descriptor_bytes']==12 and not c['full_descriptor_or_context_extent_proven']
 assert c['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and c['frozen_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and c['inline_layout_generator_sha256']==sha(ROOT/'r1/tools/recover_native_health_notification_inline_layout.py') and c['native_inline_layout_source'] and not c['source_has_instruction_byte_arrays']
 sections=allocated_sections(out/'native_health_notification_stages.o');source=(ROOT/b['units'][0]['source']).read_text()
 for body,proof in zip(c['bodies'],r['source_placement_identity_spans']):
  a=int(body['address'],16);size=body['source_span_bytes'];data=raw[a-0x27000:a-0x27000+size];assert body['size']==sum(x['size'] for x in body['instructions']) and sha(out/('disassembly-'+body['address'][2:]+'.txt'))==body['disassembly_sha256'] and 'void '+body['symbol']+'(uint32_t first' in source
  assert proof['address']==body['address'] and proof['size']==size and proof['byte_identical'] and proof['compiled_sha256']==proof['native_sha256']==hashlib.sha256(data).hexdigest() and sections['.text.'+body['symbol']][2]==size
  for token in body['inline_read_only_layout']:
   x=int(token['address'],16);native=raw[x-0x27000:x-0x27000+token['size']]
   if token['kind']=='text':assert native==token['text'].encode()+b'\0'
   elif token['kind']=='zero_padding':assert native==bytes(token['size'])
   else:assert int.from_bytes(native,'little')==token['native_value']
  n=json.loads((out/('rea-'+body['address'][2:]+'-bytes.json')).read_text())['structuredContent']['normalized_result'];assert n['complete'] and n['address']==body['address'] and n['returned_bytes']==body['size'] and bytes.fromhex(n['bytes_hex'])==raw[a-0x27000:a-0x27000+body['size']]
 for i,pair in enumerate([(0,3),(1,3),(2,3),(3,3),(4,24),(5,6)]):assert sections['.r1.health.sync.kind'+str(i)][2]==2 and sections['.r1.health.sync.kind'+str(i)][4]==hashlib.sha256(bytes(pair)).hexdigest() and raw[0x99bf4+16*i-0x27000:0x99bf6+16*i-0x27000]==bytes(pair)
 cold=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(cold)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317'
 for name,address in c['pending_bytes'].items():assert sections['.r1.health.sync.pending.'+name][2]==1 and sections['.r1.health.sync.pending.'+name][4]==hashlib.sha256(b'\0').hexdigest() and cold.read_bytes()[int(address,16)-0x200064a8]==0
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_notification_stages.py')==r['driver_sha256'] and r['comparisons']==24360 and r['counts']=={'0x8c150':1446,'0x8cd60':1446,'0x8c750':1446,'0x8baec':1446,'0x8b818':18576} and r['trace_sha256']=='726d43c022458792b95986177f34560daca594ba1ce5e31f60468f4853aa3761'
 assert len(r['source_placement_identity_spans'])==5 and r['byte_identical_source_span_bytes']==sum(x['source_span_bytes'] for x in c['bodies'])==6313
 up=json.loads((out/'upstream-reuse-candidates.json').read_text());assert up['license']=='Apache-2.0' and up['local_version']=='2.0.0' and len(up['candidates'])==3 and not up['exact_native_body_or_checkout_identity_proven'] and not up['source_is_build_input_in_this_stage']
 for p,h in up['source_files'].items():assert sha(ROOT/p)==h,p
 history=json.loads((out/'correction-history.json').read_text())
 for p,h in history['preserved_files'].items():assert sha(out/p)==h,p
 for flag in ['all_five_controller_bodies_execute','controller_full_word_provider_return_cases_checked','source_spans_include_code_typed_literals_text_and_zero_padding','heap_io_time_database_builder_and_log_are_fixtures','native_provider_addresses_are_explicit_verification_bindings','raw_r0_r3_callee_sp_typed_arguments_heap_sync_and_pending_bytes_checked']:assert r[flag]
 for flag in ['iterator_callbacks_and_builder_encoder_callbacks_executed','full_private_frame_history_verified','full_raw_abi_verified','full_descriptor_or_context_extent_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('Health sync stages:5 bodies/3400 code+native text/literals;6313 byte-identical span bytes;24360 checks;90 main imports;provider gates explicit')
if __name__=='__main__':audit()
