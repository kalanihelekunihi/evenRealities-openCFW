#!/usr/bin/env python3
"""Authenticate source subscriber registration/config and composition receipts."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-registration';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());q=json.loads((OUT/'composed-verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==q['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_subscriber_registration.py')==c['generator_sha256']
 parent=BASE/'native-subscriber-sync';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-subscriber-sync-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-subscriber-registration-runtime.o','linked_sha256','undefined_symbols'),('registration-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==78 and b['closed_parent_imports']==['r1_subscriber_roots','r1_subscriber_routes'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['typed_ram_bytes']==20
 x=c['bodies'][0];assert x['address']=='0x8af8c' and sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==146 and x['source_span_bytes']==c['native_span_bytes']==b['native_source_span_bytes']==156 and sha(OUT/'disassembly-8af8c.txt')==x['disassembly_sha256'] and allocated_sections(OUT/'native_subscriber_registration.o')['.text.r1_subscriber_register'][2]==156
 for x in v['exact_spans']:
  a=int(x['address'],16);n=x['size']
  if a<0x20000000:
   data=raw[a-0x27000:a-0x27000+n];r=json.loads((OUT/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==n and bytes.fromhex(rr['bytes_hex'])==data
  else:data=bytes(n)
  assert hashlib.sha256(data).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==3 and sum(x['size'] for x in v['exact_spans'] if int(x['address'],16)<0x20000000)==v['exact_rom_bytes']==172 and c['config']=={'r1_subscriber_roots':{'address':'0x20015708','size':20},'r1_subscriber_routes':{'address':'0x99ba8','size':16}} and c['multicast_unchecked_index_remains'] and 0x20007e04<=0x20015708<0x2001571c<=0x2003beb8
 assert sha(OUT/'report.json')==v['report_sha256']==q['report_sha256'] and sha(ROOT/'r1/tools/verify_native_subscriber_registration.py')==v['driver_sha256'] and v['comparisons']==4800 and v['counts']=={'returned':3816,'allocation_faults':984,'lock_calls':5760,'unlock_calls':3792,'allocations':5424} and v['trace_sha256']=='cb16d3091c1bbc98a38432558c3adb368052f721bfcb17c5c183510022aa444e'
 assert sha(ROOT/'r1/tools/verify_native_subscriber_composed.py')==q['driver_sha256'] and q['comparisons']==2430 and q['counts']=={'workflows':2430,'registrations':9720,'multicasts':2430,'inline_callbacks':4860,'publishes':4560} and q['trace_sha256']=='acbb63fe643c0f58172adb6a87c9385fbcf0df66a246165038e792e0363e8c85'
 for p,h in q['object_sha256s'].items():assert sha(ROOT/p)==h
 for x in q['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert sum(x['size'] for x in q['exact_spans'])==q['exact_rom_bytes']==472 and len(q['exact_spans'])==8 and q['actual_registration_multicast_and_sync_execute'] and q['heap_memmove_cmsis_publish_and_task_providers_are_fixtures'] and q['independent_list_and_route_oracle']
 assert v['independent_list_allocation_and_callback_oracle'] and v['lock_unlock_and_heap_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not q['full_private_history_or_raw_abi_verified'] and not v['whole_image_complete'] and not q['whole_image_complete'] and not v['hardware_write_executed'] and not q['hardware_write_executed']
 print('Registration:4800 direct/2430 composed comparisons,172 new/472 joint ROM bytes,20 typed RAM bytes;78 imports;provider/layout/image gates open')
if __name__=='__main__':audit()
