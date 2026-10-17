#!/usr/bin/env python3
"""Authenticate finalizer and writer/finalizer/count composition receipts."""
import hashlib,json
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-sleep-sector-finalize';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 b=json.loads((OUT/'report.json').read_text());v=json.loads((OUT/'verification.json').read_text());q=json.loads((OUT/'composed-verification.json').read_text());c=json.loads((OUT/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==q['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for u in b['units']:assert u['compiled'] and sha(ROOT/u['source'])==u['source_sha256']==c['source_sha256'] and sha(Path(u['command'][-1]))==u['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_sleep_sector_finalize.py')==c['generator_sha256']
 parent=BASE/'native-sleep-sector-write';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-sleep-sector-write-runtime.o')==b['parent_object_sha256'] and sha(BASE/'native-sleep-record/native_sleep_record.o')==v['count_parent_object_sha256']
 for file,hk,uk in [('native-sleep-sector-finalize-runtime.o','linked_sha256','undefined_symbols'),('finalizer-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(OUT/file)==b[hk] and undefined_symbols(OUT/file)[0]==b[uk]
 assert len(b['undefined_symbols'])==69 and b['closed_parent_imports']==['r1_sleep_sector_finalize'] and not b['newly_exposed_imports'] and b['new_ram_state_bytes']==c['new_ram_state_bytes']==v['new_ram_state_bytes']==q['new_ram_state_bytes']==0
 x=c['bodies'][0];assert sum(i['size'] for i in x['instructions'])==x['code_bytes']==c['native_code_bytes']==b['native_body_bytes']==192 and x['source_span_bytes']==c['native_span_bytes']==b['native_source_span_bytes']==292 and sha(OUT/'disassembly-901e4.txt')==x['disassembly_sha256'] and allocated_sections(OUT/'native_sleep_sector_finalize.o')['.text.r1_sleep_sector_finalize'][2]==292
 r=json.loads((OUT/'rea-901e4.json').read_text())['structuredContent'];rr=r['normalized_result'];a=0x901e4-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and rr['complete'] and rr['returned_bytes']==292 and bytes.fromhex(rr['bytes_hex'])==raw[a:a+292] and not c['full_context_extent_owned'] and c['io_callbacks_unresolved']
 assert sha(OUT/'report.json')==v['report_sha256']==q['report_sha256'] and sha(ROOT/'r1/tools/verify_native_sleep_sector_finalize.py')==v['driver_sha256'] and v['comparisons']==18432 and v['counts']=={'cases':18432,'reads':1603584,'writes':36864,'printf':24576,'std':18432} and v['trace_sha256']=='58bd2c851b86681f4b238729b6d76d5cbfe3713b313587d0085a772876e21521'
 assert sha(ROOT/'r1/tools/verify_native_sleep_sector_finalize_composed.py')==q['driver_sha256'] and q['comparisons']==176 and q['counts']=={'cases':176,'reads':2280,'data_writes':184,'header_writes':184,'crc':184,'finalize':224,'printf':388,'std':276,'final_writes':224} and q['trace_sha256']=='22dc69a0a30defef6899b1f61478e7d2441cf5880b996719a62ed89e98c9966d'
 for p,h in q['object_sha256s'].items():assert sha(ROOT/p)==h
 for receipt in [v,q]:
  for x in receipt['exact_spans']:
   a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==2 and sum(x['size'] for x in v['exact_spans'])==v['exact_joint_bytes']==312 and v['exact_new_bytes']==292 and v['independent_minimum_partial_read_header_and_boolean_oracle'] and v['actual_sector_count_executes'] and v['read_write_mode_and_log_providers_are_fixtures']
 assert len(q['exact_spans'])==4 and sum(x['size'] for x in q['exact_spans'])==q['exact_bytes']==1225 and q['actual_writer_finalizer_and_count_execute'] and q['io_memclear_crc_mode_and_log_are_fixtures'] and q['independent_slot_capacity_header_crc_and_log_oracle']
 assert not v['full_raw_abi_or_private_histories_verified'] and not q['full_raw_abi_or_private_histories_verified'] and not v['whole_image_complete'] and not q['whole_image_complete'] and not v['hardware_write_executed'] and not q['hardware_write_executed']
 print('Sleep finalizer:18432 direct/176 composed checks;292 new/1225 joint exact bytes;69 imports;I/O/allocator/context/private/layout/image gates open')
if __name__=='__main__':audit()
