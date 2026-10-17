#!/usr/bin/env python3
"""Authenticate native FAL partition-read source and explicit lookup/callback gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-fal-partition-read';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());d=json.loads((out/'direct-verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==d['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==d['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_fal_partition_read.py')==c['generator_sha256']
 parent=BASE/'native-flashdb-sector-read';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-flashdb-sector-read-runtime.o')==b['parent_object_sha256']
 for directory,filename,key in [('native-flashdb-sector-read','native_flashdb_sector_read.o','sector_object_sha256'),('native-flashdb-log-read','native_flashdb_log_read.o','log_object_sha256'),('native-flashdb-query-count','native_flashdb_query_count.o','count_object_sha256'),('native-flashdb-iterator','native_flashdb_iterator.o','iterator_object_sha256')]:assert sha(BASE/directory/filename)==v[key]
 for filename,hk,uk in [('native-fal-partition-read-runtime.o','linked_sha256','undefined_symbols'),('partition-read-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==89 and b['closed_parent_imports']==['r1_fdb_native_partition_read'] and b['newly_exposed_imports']==['r1_fal_native_device_by_partition']
 assert sha(out/'report.json')==v['report_sha256']==d['report_sha256'] and sha(ROOT/'r1/tools/verify_native_fal_partition_read_composed.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_fal_partition_read.py')==d['driver_sha256']
 assert v['comparisons']==948 and v['counts']=={'direct':480,'count_composed':468} and v['trace_sha256']=='d95930a9e61a83ee2a0eebd2542c3a9d32a260e85914f91fcab3de345b7d36ff'
 assert d['comparisons']==6863 and d['counts']=={'returned':6860,'assertion_loop':3,'device_read_calls':1710,'negative_callback_returns':684} and d['trace_sha256']=='87a36bd2dfa7a54ac0ad156014ad22a97da27e64c7c07ceba3f41a05132d320a'
 sections=allocated_sections(out/'native_fal_partition_read.o');x=c['bodies'][0];assert len(c['bodies'])==1 and sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==172 and x['source_span_bytes']==368 and sections['.text.'+x['symbol']][2]==368 and sha(out/'disassembly-631e8.txt')==x['disassembly_sha256']
 for name,addr,text in [('read_name',0x9c48e,b'fal_partition_read\0'),('read_missing_device',0xc0b50,b"Partition read error! Don't found flash device(%s) of the partition(%s).\0")]:assert sections['.r1.fal.'+name][2]==len(text) and sections['.r1.fal.'+name][4]==hashlib.sha256(text).hexdigest() and raw[addr-0x27000:addr-0x27000+len(text)]==text
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==16 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==1862
 r=json.loads((out/'rea-631e8.json').read_text())['structuredContent'];n=r['normalized_result'];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==368 and bytes.fromhex(n['bytes_hex'])==raw[0x631e8-0x27000:0x63358-0x27000]
 up=json.loads((out/'upstream-contracts.json').read_text());assert up['pin']=='4e5677408256f82d47cd56a6b04605dcee35ed9a' and up['license']=='Apache-2.0'
 for p,h in up['files'].items():assert sha(ROOT/p)==h,p
 assert v['actual_count_iterator_sector_log_partition_flash_adapter_status_decoder_and_callback_execute'] and v['flash_device_lookup_read_callback_memory_copy_lock_custom_callback_and_printf_are_fixtures'] and d['lookup_device_read_callback_and_printf_are_fixtures'] and d['wrapped_bounds_and_offset_fresh_reads_independently_checked'] and d['output_alias_to_partition_offset_tested'] and d['both_assertion_loops_observed']
 for r in [v,d]:assert not r['whole_image_complete'] and not r['hardware_write_executed'] and not r['full_private_history_or_raw_abi_verified']
 print('FAL partition read:6863 direct+948 composed comparisons;460 new/1862 joint verification bytes;89 imports;lookup/callback/history/image gates open')
if __name__=='__main__':audit()
