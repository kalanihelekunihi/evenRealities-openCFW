#!/usr/bin/env python3
"""Hash-bound dispatcher source, native spans and bounded fixture observations."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-get-dispatch';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 c=json.loads((OUT/'contracts.json').read_text());b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes()
 assert sha(app)==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256']
 assert sha(ROOT/'r1/tools/recover_native_health_get_dispatch.py')==c['generator_sha256'] and sha(ROOT/'r1/components/runtime/native_health_get_dispatch.c')==c['source_sha256']
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 assert sha(BASE/'native-health-latest-samples/report.json')==b['parent_report_sha256'] and sha(BASE/'native-health-latest-samples/native-health-latest-samples-runtime.o')==b['parent_object_sha256']
 assert sha(OUT/'native-health-get-dispatch-runtime.o')==b['linked_sha256'] and undefined_symbols(OUT/'native-health-get-dispatch-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==70
 assert sha(OUT/'report-source.o')==b['graph_object_sha256'] and undefined_symbols(OUT/'report-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_event_service_0008b8e8'] and b['newly_exposed_imports']==['r1_health_get_hr_encode','r1_health_get_hrv_encode','r1_health_get_spo2_encode']
 assert sha(OUT/'native_health_get_dispatch.o')==v['object_sha256']==b['units'][0]['object_sha256'] and sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_get_dispatch.py')==v['driver_sha256']
 assert c['native_code_bytes']==b['native_body_bytes']==400 and c['native_span_bytes']==b['native_source_span_bytes']==516 and b['new_ram_state_bytes']==0
 x=c['bodies'][0];assert sum(i['size'] for i in x['instructions'])==400 and sha(OUT/'disassembly-8b8e8.txt')==x['disassembly_sha256']
 assert v['comparisons']==4320 and v['trace_sha256']=='3aa30af05cabf02e08d49da8201f176d3b54faa3c712c3505f6db8d9ac88c8d6' and v['exact_bytes']==544 and sum(x['size'] for x in v['exact_spans'])==544
 for x in v['exact_spans']:
  a=int(x['address'],16);assert hashlib.sha256(raw[a-0x27000:a-0x27000+x['size']]).hexdigest()==x['sha256'];r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];n=r['normalized_result'];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==x['size'] and bytes.fromhex(n['bytes_hex'])==raw[a-0x27000:a-0x27000+x['size']]
 assert v['independent_branch_packet_and_fresh_command_oracle'] and v['all_providers_are_fixtures'] and not v['actual_getter_composition_verified'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Health get dispatcher:4320 fixture comparisons;544 exact bytes;70 imports;actual provider composition/layout/image gates open')
if __name__=='__main__':audit()
