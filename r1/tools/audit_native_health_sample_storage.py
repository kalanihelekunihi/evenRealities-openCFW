#!/usr/bin/env python3
"""Authenticate five cache aggregators and bounded cold-zero state ownership."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-health-sample-storage';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_health_sample_storage.py')==c['generator_sha256']
 parent=BASE/'native-flashdb-control';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-flashdb-control-runtime.o')==b['parent_object_sha256']
 for filename,hk,uk in [('native-health-sample-storage-runtime.o','linked_sha256','undefined_symbols'),('sample-storage-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==84 and b['closed_parent_imports']==['r1_hr_event_storage','r1_hrv_event_storage','r1_spo2_event_storage','r1_stress_event_storage','r1_temperature_event_storage'] and b['newly_exposed_imports']==['r1_health_storage_average','r1_health_storage_hour_index']
 assert sha(out/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_sample_storage.py')==v['driver_sha256'] and v['comparisons']==131365 and v['counts']=={'hr':13217,'hrv':78497,'spo2':13217,'stress':13217,'temperature':13217} and v['trace_sha256']=='3635e1ab0fe7b3e3838a9f1212a6f5e4e24d94a553123f047f99d053567e69e6'
 sections=allocated_sections(out/'native_health_sample_storage.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(out/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256'] and not x['full_cache_context_extent_proven']
  for token in x['inline_layout']:
   a=int(token['address'],16)-0x27000;data=raw[a:a+token['size']]
   if token['kind']=='word':assert int.from_bytes(data,'little')==token['value']
   elif token['kind']=='text':assert data==token['text'].encode()+b'\0'
   else:assert token['kind']=='zero' and data==bytes(token['size'])
  sec=sections['.r1.health.storage.'+x['family']];a=int(x['cache_address'],16);assert sec[2]==x['cache_prefix_bytes'] and sec[4]==hashlib.sha256(bytes(x['cache_prefix_bytes'])).hexdigest() and 0x20007e04<=a<a+x['cache_prefix_bytes']<=0x2003beb8
  r=json.loads((out/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(n['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==1136 and sum(x['source_span_bytes'] for x in c['bodies'])==2024 and c['source_prefix_bytes']==b['source_prefix_bytes']==473 and not b['full_cache_context_extents_proven']
 cold=json.loads((out/'cold-prefix-evidence.json').read_text());assert cold['scatter_zero_start']=='0x20007e04' and cold['scatter_zero_size']==0x340b4 and not cold['full_context_extents_proven'] and not cold['normal_hour_range_proven_by_storage_body']
 for p,h in cold['files'].items():assert sha(ROOT/p)==h,p
 alias=cold['known_alias'];assert int(alias['average_table_base'],16)+5*alias['row_bytes']==int(alias['row5_address'],16)==0x20016670 and alias['future_average_body_must_reuse_prefix_bytes']==8 and alias['unowned_average_rows0_through4_bytes']==40 and not alias['coupled_average_and_storage_execution_proven']
 assert int.from_bytes(raw[0x5ac70-0x27000:0x5ac74-0x27000],'little')==0x20016648 and int.from_bytes(raw[0x5bdc8-0x27000:0x5bdcc-0x27000],'little')==0x20016670
 text=c['external_stress_text'];a=int(text['address'],16)-0x27000;assert text['size']==65 and raw[a:a+65]==text['text'].encode()+b'\0' and sections['.r1.health.storage.stress_text'][4]==hashlib.sha256(raw[a:a+65]).hexdigest()
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==6 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==2089
 assert v['all_65536_hrv_values_and_all_byte_values_checked'] and v['cache_last_packet_alias_and_provider_mutation_independent_oracle'] and v['all_five_storage_bodies_execute'] and v['hour_average_and_log_are_fixtures'] and v['cache_prefix_extent_is_not_full_context']
 assert not v['full_private_history_or_raw_abi_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Sample storage:131365 comparisons;five bodies1136 code/2089 native verification bytes;473 bounded zero-prefix bytes;84 imports;hour/average/context/history/image gates open')
if __name__=='__main__':audit()
