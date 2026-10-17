#!/usr/bin/env python3
"""Authenticate sleep report handler, typed diagnostics and direct contracts."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-report';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_sleep_report.py')==c['generator_sha256']
 parent=BASE/'native-sleep-sector-finalize';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-sleep-sector-finalize-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-sleep-report-runtime.o','linked_sha256','undefined_symbols'),('report-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==68 and b['closed_parent_imports']==['r1_event_service_0008dd90'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['new_ram_state_bytes']==0
 x=c['bodies'][0];assert sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==434 and x['source_span_bytes']==c['native_span_bytes']==b['native_source_span_bytes']==964 and sha(OUT/'disassembly-8dd90.txt')==x['disassembly_sha256']
 sections=allocated_sections(OUT/'native_sleep_report.o');assert sections['.text.r1_event_service_0008dd90'][2]==964 and sections['.r1.sleep.report.components'][2]==c['external_text']['size']==65
 for a,n in [(0x8dd90,964),(0xbf8a4,65)]:
  r=json.loads((OUT/('rea-'+hex(a)[2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];offset=a-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==n and bytes.fromhex(rr['bytes_hex'])==raw[offset:offset+n]
 assert c['external_text']['address']=='0xbf8a4' and c['external_text']['text'].encode()+b'\0'==raw[0xbf8a4-0x27000:0xbf8a4-0x27000+65] and c['publish_and_storage_execution_gated']
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_sleep_report.py')==v['driver_sha256'] and v['comparisons']==9458 and v['counts']=={'cases':9456,'faults':2,'printf':66144,'std':57024,'publishes':10992,'fallbacks':4176} and v['trace_sha256']=='b9ffa4593ff556a3109f0239db406aab0d6394379e9cb873e8788318cc33e25a'
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==2 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==1029 and v['independent_fields_fresh_reads_duration_and_fallback_oracle'] and v['mode_log_publish_and_storage_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Sleep report:9458 direct checks;1029 exact bytes;68 imports;queue/storage/runtime/private/layout/image gates open')
if __name__=='__main__':audit()
