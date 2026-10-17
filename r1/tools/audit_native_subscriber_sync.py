#!/usr/bin/env python3
"""Authenticate subscriber mutex/thunk bodies and typed state configuration."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-sync';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_subscriber_sync.py')==c['generator_sha256']
 parent=BASE/'native-event-multicast';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-event-multicast-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-subscriber-sync-runtime.o','linked_sha256','undefined_symbols'),('subscriber-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==80 and b['closed_parent_imports']==['r1_subscriber_current_thread','r1_subscriber_lock','r1_subscriber_unlock'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['typed_ram_bytes']==84
 sections=allocated_sections(OUT/'native_subscriber_sync.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(OUT/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
 assert c['native_code_bytes']==b['native_body_bytes']==46 and c['native_span_bytes']==b['native_source_span_bytes']==60
 for x in v['exact_spans']:
  a=int(x['address'],16);n=x['size']
  if a<0x20000000:
   data=raw[a-0x27000:a-0x27000+n];r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==n and bytes.fromhex(rr['bytes_hex'])==data
  else:data=bytes(n)
  assert hashlib.sha256(data).hexdigest()==x['sha256']
 assert sum(x['size'] for x in v['exact_spans'] if int(x['address'],16)<0x20000000)==v['exact_rom_bytes']==88
 initialized=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(initialized)==c['initialized_data_sha256']=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and initialized.read_bytes()[0x2ec:0x2f0]==bytes(4)
 assert c['config']=={'r1_subscriber_mutex':{'address':'0x20006794','size':4},'r1_subscriber_mutex_control':{'address':'0x2001571c','size':80},'r1_subscriber_mutex_attr':{'address':'0x99bb8','size':16},'r1_subscriber_mutex_name':{'address':'0xbf784','size':12}} and 0x20007e04<=0x2001571c<0x2001576c<=0x2003beb8
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_subscriber_sync.py')==v['driver_sha256'] and v['comparisons']==13824 and v['counts']=={'lock':4608,'unlock':4608,'current':4608,'create_calls':36,'acquire_calls':9216,'release_calls':9180,'current_calls':9216} and v['trace_sha256']=='3a67e29478338accadd362102df2ebacbf7fa8acb83617857d559fad249c6499' and v['independent_state_and_call_oracle'] and v['mutex_and_task_providers_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Subscriber sync:13824 comparisons,88 exact ROM bytes,84 typed RAM bytes;three imports close;80 remain;provider/composition/layout/image gates open')
if __name__=='__main__':audit()
