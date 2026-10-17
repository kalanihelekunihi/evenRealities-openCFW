#!/usr/bin/env python3
"""Authenticate log-read/source status contracts and exposed partition boundary."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-flashdb-log-read';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());d=json.loads((out/'direct-verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==d['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256']==d['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==d['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_flashdb_log_read.py')==c['generator_sha256']
 parent=BASE/'native-flashdb-iterator';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-flashdb-iterator-runtime.o')==b['parent_object_sha256'] and sha(parent/'native_flashdb_iterator.o')==v['iterator_object_sha256'] and sha(BASE/'native-flashdb-query-count/native_flashdb_query_count.o')==v['count_object_sha256']
 for filename,hk,uk in [('native-flashdb-log-read-runtime.o','linked_sha256','undefined_symbols'),('log-read-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==90 and b['closed_parent_imports']==['r1_fdb_native_read_tsl'] and b['newly_exposed_imports']==['r1_fdb_native_partition_read']
 assert sha(out/'report.json')==v['report_sha256']==d['report_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_log_read_composed.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_log_read.py')==d['driver_sha256']
 assert v['comparisons']==948 and v['counts']=={'direct':480,'count_composed':468} and v['trace_sha256']=='edb7a58f7bc7a1f024066842541efec8a1a60be0683e61344d93a4cabd4b1017'
 assert d['comparisons']==29248 and d['counts']=={'status':3072,'flash_read':7168,'log_read':19008} and d['trace_sha256']=='30abec8ee2e8dfaa2560f9f389b2c1b4ef677e80aed297f490efa8de21634698'
 sections=allocated_sections(out/'native_flashdb_log_read.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes']==x['source_span_bytes'] and sha(out/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes']
 assert c['native_code_bytes']==b['native_body_bytes']==126
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==11 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==889
 for addr,length in [('87e14',68),('3f03e',86)]:
  r=json.loads((out/('rea-'+addr+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(addr,16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==length and bytes.fromhex(n['bytes_hex'])==raw[a:a+length]
 up=json.loads((out/'upstream-contracts.json').read_text());assert up['pin']=='4e5677408256f82d47cd56a6b04605dcee35ed9a' and up['license']=='Apache-2.0' and not up['upstream_bodies_are_compile_inputs_in_this_stage']
 for p,h in up['files'].items():assert sha(ROOT/p)==h,p
 assert v['actual_count_iterator_log_reader_flash_adapter_status_decoder_and_callback_execute'] and v['sector_reads_partition_io_memory_copy_lock_custom_callback_and_printf_are_fixtures'] and d['partition_read_is_fixture'] and d['short_read_prefix_lengths_0_through_32_checked'] and d['all_file_mode_bytes_checked'] and d['status_decoder_independent_oracle']
 for r in [v,d]:assert not r['whole_image_complete'] and not r['hardware_write_executed']
 assert not v['full_private_history_or_raw_abi_verified'] and not d['raw_full_private_histories_verified']
 print('FlashDB log reads:29248 direct+948 composed comparisons;126 new/889 joint native verification bytes;90 imports;partition/sector/history/image gates open')
if __name__=='__main__':audit()
