#!/usr/bin/env python3
"""Authenticate averaging/hour source, FP evidence and shared stress row ownership."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-health-average';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());cv=json.loads((out/'composed-verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==cv['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==cv['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_health_average.py')==c['generator_sha256']
 parent=BASE/'native-health-sample-storage';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-health-sample-storage-runtime.o')==b['parent_object_sha256'] and sha(parent/'native_health_sample_storage.o')==cv['storage_object_sha256']
 reused=out/'stress-prefix.o';assert sha(reused)==b['reused_stress_prefix_object_sha256']==v['reused_stress_prefix_object_sha256'] and sum(x[2] for x in allocated_sections(reused).values())==80
 for filename,hk,uk in [('native-health-average-runtime.o','linked_sha256','undefined_symbols'),('average-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==82 and b['closed_parent_imports']==['r1_health_storage_average','r1_health_storage_hour_index'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256']==cv['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_average.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_health_average_composed.py')==cv['driver_sha256']
 assert v['comparisons']==35151 and v['counts']=={'average':14415,'hour':20736} and v['trace_sha256']=='724db69425ca84f0f5fda9ca147180adbff6acaef73158ca34e77ee2a9714e8b'
 assert cv['comparisons']==5952 and cv['counts']=={'single_storage_calls':4800,'alias_sequence_calls':1152} and cv['sequences']==5184 and cv['trace_sha256']=='1e70d6f287b7ef2f51d95c82f108a5b177c268058696909ee17d83a7a9d5864d'
 sections=allocated_sections(out/'native_health_average.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(out/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  for token in x['inline_layout']:
   a=int(token['address'],16)-0x27000;data=raw[a:a+token['size']]
   if token['kind']=='word':assert int.from_bytes(data,'little')==token['value']
   elif token['kind']=='text':assert data==token['text'].encode()+b'\0'
   else:assert token['kind']=='zero' and data==bytes(token['size'])
  r=json.loads((out/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(n['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==182 and sum(x['source_span_bytes'] for x in c['bodies'])==242 and c['source_prefix_bytes']==b['source_prefix_bytes']==40 and c['row5_reuses_existing_stress_prefix_bytes']==b['row5_reused_stress_bytes']==8 and b['required_row5_stress_prefix_adjacency']
 assert sections['.r1.health.average.rows0_4'][2]==40 and sections['.r1.health.average.rows0_4'][4]==hashlib.sha256(bytes(40)).hexdigest() and '.r1.health.storage.stress' not in sections
 state=json.loads((out/'shared-state-evidence.json').read_text());assert state['new_rows0_through4']=={'address':'0x20016648','bytes':40,'rows':5,'row_size':8} and state['row5_alias']=={'address':'0x20016670','bytes':8,'owner':'r1_health_storage_stress_prefix','owner_total_prefix_bytes':80} and state['final_linker_adjacency_required'] and not state['whole_image_layout_proven'] and sha(parent/'cold-prefix-evidence.json')==state['parent_cold_prefix_evidence_sha256']
 assert 0x20007e04<=0x20016648<0x20016648+40==0x20016670<=0x2003beb8
 for receipt,count,size in [(v,2,242),(cv,8,2331)]:
  assert len(receipt['exact_spans'])==count and sum(x['size'] for x in receipt['exact_spans'])==receipt['exact_bytes']==size
  for x in receipt['exact_spans']:
   a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert v['rational_binary32_all_four_rounding_modes_and_count_sum_wrap_oracle'] and v['actual_average_and_hour_execute'] and v['all_calendar_hour_bytes_and_partial_outputs_checked'] and v['row5_alias_uses_existing_stress_prefix_section']
 assert cv['actual_five_storage_average_and_hour_source_bodies_execute'] and cv['hrv_stress_hrv_shared_row5_sequences_execute'] and cv['independent_coupled_cache_fp_alias_and_mutation_oracle']
 for receipt in [v,cv]:assert receipt['offset_calendar_and_log_are_fixtures'] and not receipt['full_private_history_or_raw_abi_verified'] and not receipt['whole_image_complete'] and not receipt['hardware_write_executed']
 print('Health average/hour:35151 direct+5952 composed comparisons;40 new/8 shared bytes;242 new/2331 joint verification bytes;82 imports;calendar/layout/history/image gates open')
if __name__=='__main__':audit()
