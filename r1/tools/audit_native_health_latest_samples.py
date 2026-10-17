#!/usr/bin/env python3
"""Authenticate latest-sample getters and removal of redundant cache owners."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
from build_native_health_latest_samples import symbol_rows,ALIASES,REMOVE
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-latest-samples';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());q=json.loads((OUT/'composed-verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==q['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_health_latest_samples.py')==c['generator_sha256']
 parent=BASE/'native-sleep-report';po=parent/'native-sleep-report-runtime.o';alias=OUT/'parent-cache-aliases.o';clean=OUT/'parent-shared-caches.o';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(po)==b['parent_object_sha256'] and sha(alias)==b['parent_alias_sha256'] and sha(clean)==b['parent_clean_sha256'] and allocated_sections(po)==allocated_sections(alias)
 old=symbol_rows(po);new=symbol_rows(alias)
 for name,target in ALIASES.items():
  a=next(x for x in old if x[-1]==name);z=next(x for x in new if x[-1]==name);t=next(x for x in new if x[-1]==target);assert a[:-2]==z[:-2] and z[-2]==t[-2] and a[-2] in REMOVE;old.subtract([a]);new.subtract([z])
 assert +old==+new
 expected=allocated_sections(alias);removed=sum(expected[n][2] for n in REMOVE)
 for name in REMOVE:del expected[name]
 assert removed==b['removed_orphan_prefix_bytes']==313 and allocated_sections(clean)==expected;symbols=symbol_rows(alias)
 for row in b['removed_mapping_symbols']:row=tuple(row);assert row[-1]=='$d' and row[-2] in REMOVE and symbols[row]==1;del symbols[row]
 assert symbols==symbol_rows(clean) and len(b['removed_mapping_symbols'])==3 and b['cache_aliases']==c['cache_aliases']==ALIASES and b['removed_sections']==REMOVE and b['other_allocated_sections_unchanged'] and b['other_symbol_rows_unchanged']
 for file,hk,uk in [('native-health-latest-samples-runtime.o','linked_sha256','undefined_symbols'),('latest-source.o','graph_object_sha256','graph_undefined_symbols')]:
  assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk] and not set(REMOVE)&set(allocated_sections(OUT/file))
 assert len(b['undefined_symbols'])==68 and not b['closed_parent_imports'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==0 and sha(OUT/'shared-caches.o')==b['shared_config_sha256']==v['config_sha256'] and sum(x[2] for x in allocated_sections(OUT/'shared-caches.o').values())==b['shared_existing_cache_bytes']==328
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sha(OUT/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256'];r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(n['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==216 and c['native_span_bytes']==b['native_source_span_bytes']==230
 assert sha(OUT/'report.json')==v['report_sha256']==q['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_latest_samples.py')==v['driver_sha256'] and v['comparisons']==67176 and v['counts']=={'hr':680,'spo2':680,'hrv':65816,'sample':820,'packed':66356} and v['trace_sha256']=='ada1b82de37b614a8e08115e0293892a5192d5a30446df5ef473441f0dcd4600'
 assert sha(ROOT/'r1/tools/verify_native_health_latest_samples_composed.py')==q['driver_sha256'] and q['workflows']==864
 assert q['counts']=={'workflows':864,'storage_calls':2592,'getter_calls':5184,'hour':5184,'average':5184,'logs':10368} and q['trace_sha256']=='ab525e5daf12cbe2b3a437d32d57d014b72a892bd334f48f978948dfb6db5927'
 for p,h in q['inputs'].items():assert sha(ROOT/p)==h,p
 for receipt,key,size in [(v,'exact_bytes',230),(q,'exact_bytes',1446)]:
  for x in receipt['exact_spans']:
   a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
  assert sum(x['size'] for x in receipt['exact_spans'])==receipt[key]==size
 assert v['independent_sequential_copy_zero_and_alias_oracle'] and v['all_hrv_values_and_byte_sample_values_checked'] and v['actual_nested_getters_execute'] and v['existing_cache_owners_and_aliases_verified'] and q['actual_storage_packed_and_public_getters_execute'] and q['one_source_owner_per_hr_spo2_hrv_cache'] and q['hour_average_mode_and_log_providers_are_fixtures'] and q['independent_sequential_cache_and_sample_oracle']
 assert not v['full_raw_abi_or_private_histories_verified'] and not q['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not q['whole_image_complete'] and not v['hardware_write_executed'] and not q['hardware_write_executed']
 print('Latest samples:67176 direct/864 storage workflows;230 new/1446 joint exact bytes;313 duplicate backing bytes removed;328 existing bytes shared;68 imports;provider/layout/image gates open')
if __name__=='__main__':audit()
