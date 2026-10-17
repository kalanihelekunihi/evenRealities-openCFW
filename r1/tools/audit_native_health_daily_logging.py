#!/usr/bin/env python3
"""Authenticate daily cache logging tails and fixture composition evidence."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-daily-logging';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());q=json.loads((OUT/'composed-verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==q['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_health_daily_logging.py')==c['generator_sha256']
 parent=BASE/'native-health-daily-fixture';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-health-daily-fixture-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-health-daily-logging-runtime.o','linked_sha256','undefined_symbols'),('logging-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==76 and b['closed_parent_imports']==['r1_health_fixture_notify_hr','r1_health_fixture_notify_spo2','r1_health_fixture_notify_temperature'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==0
 sections=allocated_sections(OUT/'native_health_daily_logging.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(OUT/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(rr['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==562 and c['native_span_bytes']==b['native_source_span_bytes']==912 and not c['full_daily_cache_extent_owned'] and c['daily_logging_tails_execute']
 for x in c['bodies']:assert [d['value'] for d in x['data'] if d['kind']=='word']==['__start_log_const_data+224','__start_log_const_data']
 assert sha(OUT/'report.json')==v['report_sha256']==q['report_sha256'] and sha(ROOT/'r1/tools/verify_native_health_daily_logging.py')==v['driver_sha256'] and v['comparisons']==7104 and v['counts']=={'cases':7104,'printf':142080,'std2':3840,'std4':103680,'mode_calls':482304} and v['trace_sha256']=='80be66fbedb0966e93fd6665a3cbb4f9e94a43ceff49f724b1580dec15d5a7fe'
 for receipt in [v,q]:
  for x in receipt['exact_spans']:
   a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==3 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==912 and v['independent_log_order_arguments_and_stack_oracle'] and v['cache_mode_and_log_providers_are_fixtures'] and v['fresh_cache_after_mode_mutations_checked']
 assert sha(ROOT/'r1/tools/verify_native_health_daily_logging_composed.py')==q['driver_sha256'] and q['comparisons']==576 and q['counts']=={'cases':576,'getter':0,'random_calls':16704,'notifications':768,'cache_gets':6336} and q['logs']=={'0x91638':15264,'0x799f8':9792,'0x799d6':384} and q['trace_sha256']=='d9f0929098ae6e965cfb058b36fd99c351f1160457e48ea2e1b73ee5449cf695' and not q['temperature_accessor_executes_in_direct_getter_cases']
 for p,h in q['object_sha256s'].items():assert sha(ROOT/p)==h
 assert len(q['exact_spans'])==5 and sum(x['size'] for x in q['exact_spans'])==q['exact_bytes']==2104 and q['actual_fixture_and_three_logging_tails_execute'] and q['time_cache_random_mode_and_log_providers_are_fixtures'] and q['independent_hour_range_signed_random_and_cache_oracle']
 assert not v['full_cache_extent_owned'] and not q['full_daily_cache_extent_owned'] and not v['full_raw_abi_or_private_histories_verified'] and not q['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not q['whole_image_complete'] and not v['hardware_write_executed'] and not q['hardware_write_executed']
 print('Daily logging:7104 direct/576 composed comparisons;912 new/2104 joint bytes;76 imports;provider/cache/layout/image gates open')
if __name__=='__main__':audit()
