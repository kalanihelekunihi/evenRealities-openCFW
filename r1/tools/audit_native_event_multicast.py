#!/usr/bin/env python3
"""Authenticate multicast source and scoped emulator receipts without Unicorn."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-event-multicast';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_event_multicast.py')==c['generator_sha256']
 parent=BASE/'native-time-update';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-time-update-runtime.o')==b['parent_object_sha256']
 for file,hkey,ukey in [('native-event-multicast-runtime.o','linked_sha256','undefined_symbols'),('multicast-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hkey] and undefined_symbols(OUT/file)[0]==b[ukey]
 assert len(b['undefined_symbols'])==83 and b['closed_parent_imports']==['r1_event_service_0008b028'] and b['newly_exposed_imports']==['r1_subscriber_current_thread','r1_subscriber_lock','r1_subscriber_roots','r1_subscriber_routes','r1_subscriber_unlock'] and b['new_ram_state_bytes']==0
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_event_multicast.py')==v['driver_sha256'] and v['comparisons']==4550 and v['counts']=={'cases':4550,'callbacks':6396,'publishes':4824,'copies':9514,'allocations':8292} and v['trace_sha256']=='8c42436d0200be674b83d2a57cc0dbc87c8c5ca164d298a7a7050bca2d88f86d'
 x=c['bodies'][0];assert x['address']=='0x8b028' and x['code_bytes']==202 and x['source_span_bytes']==212 and sum(i['size'] for i in x['instructions'])==202 and sha(OUT/'disassembly-8b028.txt')==x['disassembly_sha256'] and allocated_sections(OUT/'native_event_multicast.o')['.text.r1_event_service_0008b028'][2]==212
 r=json.loads((OUT/'rea-8b028.json').read_text())['structuredContent'];n=r['normalized_result'];native=raw[0x8b028-0x27000:0x8b0fc-0x27000];assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==212 and bytes.fromhex(n['bytes_hex'])==native and hashlib.sha256(native).hexdigest()==v['exact_span_sha256'] and v['exact_bytes']==212
 assert v['independent_traversal_and_copy_oracle'] and v['providers_and_callbacks_are_fixtures'] and not v['full_private_history_or_raw_abi_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Multicast:4550 comparisons,212 exact bytes,83 unresolved imports; provider/configuration/composition/layout/image gates open')
if __name__=='__main__':audit()
