#!/usr/bin/env python3
"""Authenticate destructive consumer and full local subscriber delivery chain."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-subscriber-consume';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());q=json.loads((OUT/'delivery-verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==q['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_subscriber_consume.py')==c['generator_sha256']
 parent=BASE/'native-subscriber-registration';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-subscriber-registration-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-subscriber-consume-runtime.o','linked_sha256','undefined_symbols'),('consume-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==77 and b['closed_parent_imports']==['r1_event_service_0008b0fc'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==0
 x=c['bodies'][0];assert x['address']=='0x8b0fc' and sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==58 and x['source_span_bytes']==c['native_span_bytes']==b['native_source_span_bytes']==60 and sha(OUT/'disassembly-8b0fc.txt')==x['disassembly_sha256'] and allocated_sections(OUT/'native_subscriber_consume.o')['.text.r1_event_service_0008b0fc'][2]==60
 r=json.loads((OUT/'rea-8b0fc.json').read_text())['structuredContent'];rr=r['normalized_result'];data=raw[0x8b0fc-0x27000:0x8b138-0x27000];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==60 and bytes.fromhex(rr['bytes_hex'])==data and hashlib.sha256(data).hexdigest()==v['exact_span_sha256'] and v['exact_bytes']==60
 assert sha(OUT/'report.json')==v['report_sha256']==q['report_sha256'] and sha(ROOT/'r1/tools/verify_native_subscriber_consume.py')==v['driver_sha256'] and v['comparisons']==27651 and v['counts']=={'returned':20397,'faults':7254,'callbacks':7956,'locks':27654,'unlocks':13146,'current_calls':27654} and v['trace_sha256']=='6245c4629c9cd78a816ef26442d139521a57c2599af18df8b44c0c5b57cdb6c5'
 assert sha(ROOT/'r1/tools/verify_native_subscriber_delivery.py')==q['driver_sha256'] and q['comparisons']==2430 and q['counts']=={'workflows':2430,'registrations':9720,'multicasts':2430,'inline_callbacks':4860,'publishes':4560,'consumers':4560,'consumed_callbacks':6480} and q['trace_sha256']=='f6ced5bbef35f6c452a9224fce41f5c8a54842e6c30307eb1796a4573053bafb'
 for p,h in q['object_sha256s'].items():assert sha(ROOT/p)==h
 for x in q['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert sum(x['size'] for x in q['exact_spans'])==q['exact_rom_bytes']==532 and len(q['exact_spans'])==9 and q['actual_registration_multicast_sync_and_consumer_execute'] and q['heap_memmove_cmsis_publish_and_task_providers_are_fixtures'] and q['independent_list_and_route_oracle']
 assert v['independent_traversal_and_mutation_oracle'] and v['lock_unlock_current_and_callbacks_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not q['full_private_history_or_raw_abi_verified'] and not v['whole_image_complete'] and not q['whole_image_complete'] and not v['hardware_write_executed'] and not q['hardware_write_executed']
 print('Subscriber consumer:27651 direct/2430 composed comparisons;60 new/532 joint ROM bytes;77 imports;provider/scheduling/layout/image gates open')
if __name__=='__main__':audit()
