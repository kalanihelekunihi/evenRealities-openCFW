#!/usr/bin/env python3
"""Authenticate activity packed-delta storage and source calendar composition."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-activity-storage';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());cv=json.loads((out/'composed-verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==cv['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==cv['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_activity_storage.py')==c['generator_sha256']
 parent=BASE/'native-calendar-frames';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-calendar-frames-runtime.o')==b['parent_object_sha256'] and sha(parent/'native_calendar_frames.o')==cv['calendar_object_sha256'] and sha(parent/'shared-calendar-config.o')==cv['shared_calendar_config_sha256']
 reused=out/'activity-cache.o';assert sha(reused)==b['reused_activity_cache_object_sha256']==v['reused_activity_cache_object_sha256']==cv['reused_activity_cache_object_sha256'];rs=allocated_sections(reused);assert sum(x[2] for x in rs.values())==b['reused_activity_config_bytes']==584 and rs['.r1.health.cache.activity'][4]==hashlib.sha256(bytes(584)).hexdigest()
 symbols={p[-1]:p[:-1] for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(reused)],text=True).splitlines() if len(p:=line.split())==4}
 assert symbols['r1_cache_activity'][:2]==['00000000','00000240'] and symbols['r1_daily_activity_offset'][:2]==['00000240','00000002'] and symbols['r1_daily_activity_timestamp'][:2]==['00000244','00000004'] and b['reused_activity_cache_bytes']==c['reused_activity_cache_bytes']==576 and b['new_ram_state_bytes']==0
 for filename,hk,uk in [('native-activity-storage-runtime.o','linked_sha256','undefined_symbols'),('activity-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==81 and b['closed_parent_imports']==['r1_activity_event_storage'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256']==cv['report_sha256'] and sha(ROOT/'r1/tools/verify_native_activity_storage.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_activity_storage_composed.py')==cv['driver_sha256']
 assert v['comparisons']==88406 and v['counts']=={'storage':86117,'bucket':2289} and v['trace_sha256']=='216dd79df3b7e5729f41e2e9e67a20cf7c572e4f7d2c58402df54f9a07fe3d66'
 assert cv['comparisons']==3744 and cv['counts']=={'storage':3744} and cv['trace_sha256']=='ff31b6eefab6264fc6aaaa2e02242f35cd62cf4635048a612639c68e745395d7'
 sections=allocated_sections(out/'native_activity_storage.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(out/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  for token in x['inline_layout']:
   a=int(token['address'],16)-0x27000;data=raw[a:a+token['size']]
   if token['kind']=='word':assert int.from_bytes(data,'little')==token['value']
   elif token['kind']=='text':assert data==token['text'].encode()+b'\0'
   else:assert token['kind']=='zero' and data==bytes(token['size'])
  r=json.loads((out/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(n['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==296 and sum(x['source_span_bytes'] for x in c['bodies'])==394
 for name,a,size in [('multi_ring',0xbf92c,81),('multi_sdk',0xbf980,75)]:assert sections['.r1.activity.'+name][2]==size and sections['.r1.activity.'+name][4]==hashlib.sha256(raw[a-0x27000:a-0x27000+size]).hexdigest()
 for receipt,count,size in [(v,4,550),(cv,8,902)]:
  assert len(receipt['exact_spans'])==count and sum(x['size'] for x in receipt['exact_spans'])==receipt['exact_bytes']==size
  for x in receipt['exact_spans']:
   a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert v['all_65536_byte_bucket_pairs_checked'] and v['bucket_is_fixture_for_storage_and_calendar_is_fixture_for_bucket']
 assert cv['actual_storage_bucket_offset_calendar_unix_source_chain_executes'] and not cv['calendar_or_bucket_provider_is_fixture'] and cv['timezone_packet_updates_and_logging_are_controlled_fixtures']
 for receipt in [v,cv]:assert receipt['packed_12_10_10_counter_wrap_and_alias_independent_oracle'] and receipt['whole_delta_deposited_in_start_bucket_preserved'] and not receipt['full_private_history_or_raw_abi_verified'] and not receipt['whole_image_complete'] and not receipt['hardware_write_executed']
 print('Activity storage:88406 direct+3744 source-calendar comparisons;584 existing config bytes;550 new/902 joint verification bytes;81 imports;caller/runtime/layout/image gates open')
if __name__=='__main__':audit()
