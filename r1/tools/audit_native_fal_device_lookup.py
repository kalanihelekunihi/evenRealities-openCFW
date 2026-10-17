#!/usr/bin/env python3
"""Authenticate FAL lookup and reuse of pinned initializer-owned state."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-fal-device-lookup';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());d=json.loads((out/'direct-verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==d['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==d['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_fal_device_lookup.py')==c['generator_sha256']
 parent=BASE/'native-fal-partition-read';po=parent/'native-fal-partition-read-runtime.o';clone=out/'parent-shared-state.o';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(po)==b['parent_object_sha256'] and sha(clone)==b['parent_shared_state_clone_sha256'] and allocated_sections(po)==allocated_sections(clone)
 old=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(po)],text=True).splitlines());new=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(clone)],text=True).splitlines())
 for n,size in zip(b['globalized_existing_state_symbols'],[4,4,28]):
  row=('00000000','%08x'%size,'b',n);assert old[row]==1 and new[(row[0],row[1],'B',n)]==1;del old[row];del new[(row[0],row[1],'B',n)]
 assert old==new and b['globalized_existing_state_symbols']==['r1_fal_partition_table','r1_fal_partition_count','r1_fal_partition_cache']
 shared=out/'shared-state.o';assert sha(shared)==b['shared_state_object_sha256']==v['shared_state_object_sha256']==d['shared_state_object_sha256'] and sum(x[2] for x in allocated_sections(shared).values())==b['shared_existing_state_bytes']==36 and b['new_ram_state_bytes']==0 and b['required_table_count_native_adjacency_gate']
 for directory,filename,key in [('native-fal-partition-read','native_fal_partition_read.o','partition_object_sha256'),('native-flashdb-sector-read','native_flashdb_sector_read.o','sector_object_sha256'),('native-flashdb-log-read','native_flashdb_log_read.o','log_object_sha256'),('native-flashdb-query-count','native_flashdb_query_count.o','count_object_sha256'),('native-flashdb-iterator','native_flashdb_iterator.o','iterator_object_sha256')]:assert sha(BASE/directory/filename)==v[key]
 for filename,hk,uk in [('native-fal-device-lookup-runtime.o','linked_sha256','undefined_symbols'),('lookup-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==88 and b['closed_parent_imports']==['r1_fal_native_device_by_partition'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256']==d['report_sha256'] and sha(ROOT/'r1/tools/verify_native_fal_device_lookup_composed.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_fal_device_lookup.py')==d['driver_sha256']
 assert v['comparisons']==948 and v['counts']=={'direct':480,'count_composed':468} and v['trace_sha256']=='c46935da21c015acf9d0175a67d1bc721cb030f0de7a3b8450b3a8d443da4a8c'
 assert d['comparisons']==17370 and d['counts']=={'returned':6939,'lower_assert':1950,'upper_assert':8481,'unaligned_returned':6804} and d['trace_sha256']=='116d81d66988e97a11873b2063ddf9179201915a01b66eb5b1a9cfbcebaa606f'
 sections=allocated_sections(out/'native_fal_device_lookup.o');x=c['bodies'][0];assert len(c['bodies'])==1 and sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==58 and x['source_span_bytes']==180 and sections['.text.'+x['symbol']][2]==180 and sha(out/'disassembly-64f74.txt')==x['disassembly_sha256']
 text=b'flash_device_find_by_part\0';assert sections['.r1.fal.lookup_name'][2]==26 and sections['.r1.fal.lookup_name'][4]==hashlib.sha256(text).hexdigest() and raw[0x9c43f-0x27000:0x9c459-0x27000]==text
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==18 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==2068
 r=json.loads((out/'rea-64f74.json').read_text())['structuredContent'];n=r['normalized_result'];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==180 and bytes.fromhex(n['bytes_hex'])==raw[0x64f74-0x27000:0x65028-0x27000]
 up=json.loads((out/'upstream-contracts.json').read_text());assert up['pin']=='4e5677408256f82d47cd56a6b04605dcee35ed9a' and up['license']=='Apache-2.0' and sha(BASE/'sdk-fal-partition/report.json')==up['initializer_owner_report_sha256'] and sha(BASE/'sdk-fal-partition/verification.json')==up['initializer_verification_sha256'] and sum(x['bytes'] for x in up['existing_state_owners'].values())==36
 for p,h in up['files'].items():assert sha(ROOT/p)==h,p
 assert v['actual_count_iterator_sector_log_partition_lookup_flash_status_and_callback_execute'] and v['device_read_callback_memory_copy_lock_custom_callback_and_printf_are_fixtures'] and d['native_lookup_executes_with_actual_initializer_owned_state_sections'] and d['cache_words_are_runtime_fixtures'] and d['inclusive_range_and_unaligned_floor_index_independent_oracle'] and d['final_table_count_adjacency_is_not_yet_linked_image_proof']
 for r in [v,d]:assert not r['whole_image_complete'] and not r['hardware_write_executed'] and not r['full_private_history_or_raw_abi_verified']
 print('FAL lookup:17370 direct+948 composed comparisons;36 existing state bytes reused;206 new/2068 joint verification bytes;88 imports;callback/layout/history/image gates open')
if __name__=='__main__':audit()
