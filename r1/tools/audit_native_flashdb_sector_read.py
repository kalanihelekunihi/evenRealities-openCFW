#!/usr/bin/env python3
"""Authenticate sector parsing, assertion/text ownership and composed source evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-flashdb-sector-read';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());d=json.loads((out/'direct-verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==d['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==d['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_flashdb_sector_read.py')==c['generator_sha256']
 parent=BASE/'native-flashdb-log-read';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-flashdb-log-read-runtime.o')==b['parent_object_sha256'] and sha(parent/'native_flashdb_log_read.o')==v['log_object_sha256']==d['log_object_sha256'] and sha(BASE/'native-flashdb-query-count/native_flashdb_query_count.o')==v['count_object_sha256']==d['count_object_sha256'] and sha(BASE/'native-flashdb-iterator/native_flashdb_iterator.o')==v['iterator_object_sha256']
 for filename,hk,uk in [('native-flashdb-sector-read-runtime.o','linked_sha256','undefined_symbols'),('sector-read-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==89 and b['closed_parent_imports']==['r1_fdb_native_read_sector'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256']==d['report_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_sector_read_composed.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_sector_read.py')==d['driver_sha256']
 assert v['comparisons']==948 and v['counts']=={'direct':480,'count_composed':468} and v['trace_sha256']=='67e475f08201cd396de57213dea1a20fb3c5b9572b59b7509f5780f02679c42d'
 assert d['comparisons']==9615 and sum(d['counts'].values())==9615 and d['counts']=={'returned':9532,'assertion_loop':83} and d['trace_sha256']=='8aef0cd879ce9bd2acdf08f8bb02bfe0b8c3ae5a2933e8b1a5701718fc594f76'
 sections=allocated_sections(out/'native_flashdb_sector_read.o');x=c['bodies'][0];assert len(c['bodies'])==1 and sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==360 and x['source_span_bytes']==496 and sections['.text.'+x['symbol']][2]==496 and sha(out/'disassembly-87c24.txt')==x['disassembly_sha256']
 assert sections['.r1.fdb.sector_function_name'][2]==17 and sections['.r1.fdb.sector_function_name'][4]==hashlib.sha256(b'read_sector_info\0').hexdigest() and raw[0x9bdb9-0x27000:0x9bdca-0x27000]==b'read_sector_info\0'
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==13 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==1402
 r=json.loads((out/'rea-87c24.json').read_text())['structuredContent'];n=r['normalized_result'];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==496 and bytes.fromhex(n['bytes_hex'])==raw[0x87c24-0x27000:0x87e14-0x27000]
 up=json.loads((out/'upstream-contracts.json').read_text());assert up['pin']=='4e5677408256f82d47cd56a6b04605dcee35ed9a' and up['license']=='Apache-2.0'
 for p,h in up['files'].items():assert sha(ROOT/p)==h,p
 assert v['actual_count_iterator_sector_log_flash_adapter_status_decoder_and_callback_execute'] and v['partition_io_memory_copy_lock_custom_callback_and_printf_are_fixtures'] and d['partition_and_printf_are_fixtures'] and d['actual_log_flash_status_and_db_path_execute'] and d['all_0_through_80_header_prefix_lengths_checked'] and d['both_native_assertion_loops_observed'] and d['independent_sector_layout_space_and_return_oracle']
 for r in [v,d]:assert not r['whole_image_complete'] and not r['hardware_write_executed'] and not r['full_private_history_or_raw_abi_verified']
 print('FlashDB sector:9615 direct+948 composed comparisons;513 new/1402 joint verification bytes;89 imports;partition/history/image gates open')
if __name__=='__main__':audit()
