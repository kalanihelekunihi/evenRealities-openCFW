#!/usr/bin/env python3
"""Authenticate local daily diagnostic fixture and reused PRNG provider."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-daily-fixture';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_health_daily_fixture.py')==c['generator_sha256']
 parent=BASE/'native-subscriber-consume';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-subscriber-consume-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-health-daily-fixture-runtime.o','linked_sha256','undefined_symbols'),('fixture-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==79 and b['closed_parent_imports']==['r1_event_service_0008b378'] and b['newly_exposed_imports']==['r1_health_fixture_notify_hr','r1_health_fixture_notify_spo2','r1_health_fixture_notify_temperature'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==0
 assert sha(OUT/'selected-rand.o')==b['reused_rand_object_sha256'] and sha(BASE/'native-libc-primitives/report.json')==b['reused_rand_report_sha256'] and not undefined_symbols(OUT/'selected-rand.o')[0]
 sections=allocated_sections(OUT/'native_health_daily_fixture.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(OUT/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(rr['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==786 and c['native_span_bytes']==b['native_source_span_bytes']==1192 and not c['full_daily_cache_extent_owned'] and c['notification_tails_are_explicit_imports']
 assert c['bodies'][0]['data'][0]=={'address':'0x8b688','size':4,'kind':'word','value':'__start_log_const_data+224'} and c['bodies'][0]['data'][1]=={'address':'0x8b68c','size':4,'kind':'word','value':'__start_log_const_data'}
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_daily_fixture.py')==v['driver_sha256'] and v['comparisons']==13568 and v['counts']=={'cases':13312,'getter':256,'random_calls':144000,'notifications':6192,'cache_gets':54144} and v['logs']=={'0x91638':24576,'0x799f8':9240,'0x799c0':5120,'0x799c8':2024} and v['trace_sha256']=='87e3d2d823d862b46af376c51e7d69ad9af3280bc6bd3c23e2ce69df2ecad43f'
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==2 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==1192 and v['independent_hour_range_signed_random_and_cache_oracle'] and v['logging_time_cache_random_and_notification_providers_are_fixtures'] and v['temperature_accessor_executes_in_direct_getter_cases'] and not v['full_daily_cache_extent_owned'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Daily fixture:13568 comparisons,1192 exact verification bytes;reused source rand;79 imports;notification/cache/log/config/provider/image gates open')
if __name__=='__main__':audit()
