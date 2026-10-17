#!/usr/bin/env python3
"""Authenticate sleep record/retry/erase source and existing shared context."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-record';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_sleep_record.py')==c['generator_sha256']
 parent=BASE/'native-sleep-sync-status';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-sleep-sync-status-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-sleep-record-runtime.o','linked_sha256','undefined_symbols'),('record-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==72 and b['closed_parent_imports']==['r1_event_service_0008dc94','r1_event_service_0008dd88'] and b['newly_exposed_imports']==['r1_sleep_sector_fallback','r1_sleep_sector_select','r1_sleep_sector_write'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['new_ram_state_bytes']==0
 sections=allocated_sections(OUT/'native_sleep_record.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(OUT/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(rr['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==482 and c['native_span_bytes']==b['native_source_span_bytes']==924 and not c['full_context_extent_owned'] and c['sector_providers_unresolved']
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_sleep_record.py')==v['driver_sha256'] and v['comparisons']==17429 and v['counts']=={'store':7936,'event':7941,'erase':516,'erase_event':516,'sector_count':520,'selects':11400,'fallbacks':3462,'writes':11400,'erases':266616,'throttles':3108} and v['trace_sha256']=='9de7683eb021e5814238d31c060ba8a9522dd349aa478e790076fee4c75609f0'
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==5 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==924 and v['independent_retry_size_sector_and_log_oracle'] and v['actual_event_store_erase_and_count_execute'] and v['sector_alloc_write_log_erase_and_throttle_providers_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Sleep record/retry/event/erase/count:924 exact verification bytes;72 imports;sector/context/provider/layout/image gates open')
if __name__=='__main__':audit()
