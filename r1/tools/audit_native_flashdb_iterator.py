#!/usr/bin/env python3
"""Authenticate TSDB iterator source, REA spans, composition and explicit gates."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-flashdb-iterator';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_flashdb_iterator.py')==c['generator_sha256']
 parent=BASE/'native-flashdb-query-count';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-flashdb-query-count-runtime.o')==b['parent_object_sha256'] and sha(parent/'native_flashdb_query_count.o')==v['count_object_sha256']
 for filename,hashkey,ukey in [('native-flashdb-iterator-runtime.o','linked_sha256','undefined_symbols'),('iterator-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hashkey] and undefined_symbols(out/filename)[0]==b[ukey]
 assert len(b['undefined_symbols'])==90 and b['closed_parent_imports']==['r1_health_sync_provider_00063ad8'] and b['newly_exposed_imports']==['r1_fdb_native_read_sector','r1_fdb_native_read_tsl']
 assert sha(out/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_flashdb_iterator.py')==v['driver_sha256'] and v['comparisons']==948 and v['counts']=={'direct':480,'count_composed':468} and v['trace_sha256']=='098af14c04c1c84ff87f5f90b3586bfa9b2b545eb6ea29b2d494a8bd32b4a190'
 sections=allocated_sections(out/'native_flashdb_iterator.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sha(out/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  assert sections['.text.'+x['symbol']][2]==x['source_span_bytes']
 assert c['native_code_bytes']==b['native_body_bytes']==508 and sum(x['source_span_bytes'] for x in c['bodies'])==592
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==8 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==763
 for addr,length in [('63ad8',476),('6a158',116)]:
  r=json.loads((out/('rea-'+addr+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(addr,16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==length and bytes.fromhex(n['bytes_hex'])==raw[a:a+length]
 assert v['actual_count_iterator_navigation_and_count_callback_execute'] and v['sector_log_reads_memory_copy_lock_custom_callback_and_printf_are_fixtures']
 assert not v['full_private_history_or_raw_abi_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed'] and not b['whole_image_complete']
 print('FlashDB iterator:948 cases incl468 actual count compositions;592 new/763 joint exact verification bytes;90 imports;read/provider/history/image gates open')
if __name__=='__main__':audit()
