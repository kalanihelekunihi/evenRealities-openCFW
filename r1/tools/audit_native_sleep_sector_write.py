#!/usr/bin/env python3
"""Authenticate complete contiguous sleep writer and typed external success text."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sector-write';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_sleep_sector_write.py')==c['generator_sha256']
 parent=BASE/'native-sleep-sector-select';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-sleep-sector-select-runtime.o')==b['parent_object_sha256']
 for file,hk,uk in [('native-sleep-sector-write-runtime.o','linked_sha256','undefined_symbols'),('writer-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==70 and b['closed_parent_imports']==['r1_sleep_sector_write'] and b['newly_exposed_imports']==['r1_sleep_sector_finalize'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['new_ram_state_bytes']==0
 x=c['bodies'][0];assert sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==508 and x['source_span_bytes']==c['native_span_bytes']==b['native_source_span_bytes']==844 and sha(OUT/'disassembly-8fe98.txt')==x['disassembly_sha256']
 sections=allocated_sections(OUT/'native_sleep_sector_write.o');assert sections['.text.r1_sleep_sector_write'][2]==844 and sections['.r1.sleep.write.success'][2]==c['external_text']['size']==69
 for a,n in [(0x8fe98,844),(0xbfaf8,69)]:
  r=json.loads((OUT/('rea-'+hex(a)[2:]+'.json')).read_text())['structuredContent'];rr=r['normalized_result'];offset=a-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==n and bytes.fromhex(rr['bytes_hex'])==raw[offset:offset+n]
 assert c['external_text']['address']=='0xbfaf8' and c['external_text']['text'].encode()+b'\0'==raw[0xbfaf8-0x27000:0xbfaf8-0x27000+69] and not c['full_context_extent_owned'] and c['finalizer_unresolved'] and c['contiguous_success_code_beyond_frozen_range_included']
 assert sha(OUT/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_sleep_sector_write.py')==v['driver_sha256'] and v['comparisons']==5760 and v['counts']=={'cases':5760,'reads':68544,'data_writes':4800,'header_writes':4128,'crc':4128,'finalize':3360,'printf':4320,'std':3168} and v['trace_sha256']=='d0c9ffba5c29cb44c7d82caad87c734c69f0feb2bec07934b4438dd633e9e4bf'
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==2 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==913 and v['independent_slot_capacity_header_crc_and_log_oracle'] and v['io_memclear_crc_mode_log_and_finalizer_are_fixtures'] and not v['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Sleep writer:913 exact verification bytes;70 imports;finalizer/I/O/CRC/context/private/layout/image gates open')
if __name__=='__main__':audit()
