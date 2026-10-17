#!/usr/bin/env python3
"""Authenticate two native read frames while preserving unrelated source providers."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-internal-flash-read-frames';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());d=json.loads((out/'direct-verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==d['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==d['object_sha256']
 parent=BASE/'native-fal-read-frames';po=parent/'native-fal-read-frames-runtime.o';clone=out/'parent-read-weakened.o';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(po)==b['parent_object_sha256'] and sha(clone)==b['weakened_parent_sha256'] and allocated_sections(po)==allocated_sections(clone)
 old=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(po)],text=True).splitlines());new=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(clone)],text=True).splitlines())
 assert b['replacement_symbols']==['r1_internal_flash_device_read','r1_internal_flash_mapped_read']
 for n,size in zip(b['replacement_symbols'],[64,30]):
  row=('00000000','%08x'%size,'T',n);assert old[row]==1 and new[(row[0],row[1],'W',n)]==1;del old[row];del new[(row[0],row[1],'W',n)]
 assert old==new and b['parent_allocated_sections_unchanged'] and b['parent_other_symbols_unchanged']
 parent_sections=allocated_sections(po);assert parent_sections['.r1.flash.record'][2]==80 and parent_sections['.r1.flash.fstorage'][2]==20 and b['shared_existing_state_bytes']==100 and b['new_ram_state_bytes']==0
 for directory,filename,key in [('native-fal-read-frames','native_fal_read_frames.o','fal_frame_object_sha256'),('native-fal-read-frames','read-state.o','read_state_object_sha256'),('native-fal-device-lookup','native_fal_device_lookup.o','lookup_object_sha256'),('native-fal-device-lookup','shared-state.o','shared_state_object_sha256'),('native-fal-partition-read','native_fal_partition_read.o','partition_object_sha256'),('native-flashdb-sector-read','native_flashdb_sector_read.o','sector_object_sha256'),('native-flashdb-log-read','native_flashdb_log_read.o','log_object_sha256'),('native-flashdb-query-count','native_flashdb_query_count.o','count_object_sha256'),('native-flashdb-iterator','native_flashdb_iterator.o','iterator_object_sha256')]:assert sha(BASE/directory/filename)==v[key]
 for filename,hk,uk in [('native-internal-flash-read-frames-runtime.o','linked_sha256','undefined_symbols'),('internal-read-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==88 and not b['closed_parent_imports'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256']==d['report_sha256'] and sha(ROOT/'r1/tools/verify_native_internal_flash_read_frames_composed.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_internal_flash_read_frames.py')==d['driver_sha256']
 assert v['comparisons']==948 and v['counts']=={'direct':480,'count_composed':468} and v['trace_sha256']=='8d4d6642a665504af206b000cc53c4011e890b94cfe7a270f0972aeca8436528'
 assert d['comparisons']==3420 and d['counts']=={'policy':3024,'copy':396,'faults':420,'before_calls':336,'after_calls':252} and d['trace_sha256']=='568c8992b819502351b30b284761100f137a1ed75209bd1d45560f757019de79'
 sections=allocated_sections(out/'native_internal_flash_read_frames.o');assert sections['.text.r1_internal_flash_device_read'][2]==64 and sections['.text.r1_internal_flash_mapped_read'][2]==28 and b['native_body_bytes']==82 and b['native_source_span_bytes']==92
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==22 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==2226
 for address,length in [('54a4c',64),('5c464',28)]:
  r=json.loads((out/('rea-'+address+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(address,16)-0x27000;assert r['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and n['complete'] and n['returned_bytes']==length and bytes.fromhex(n['bytes_hex'])==raw[a:a+length]
 assert v['actual_tsdb_fal_registry_flash_policy_and_mapped_copy_source_chain_executes'] and v['flash_contents_are_emulator_data_fixtures'] and not v['read_io_provider_is_fixture'] and v['memory_copy_lock_custom_callback_and_printf_are_fixtures'] and d['actual_read_policy_and_mapped_copy_execute'] and not d['read_io_provider_is_fixture'] and d['mapped_data_and_before_after_callbacks_are_fixtures'] and d['bytewise_overlap_low16_length_and_callback_mutation_oracle'] and d['native_null_callback_faults_retained'] and d['shared_state_native_addresses_are_verification_bindings']
 for r in [v,d]:assert not r['whole_image_complete'] and not r['hardware_write_executed'] and not r['full_private_history_or_raw_abi_verified']
 print('Internal flash read:3420 direct+948 composed comparisons;100 existing state bytes;92 new/2226 joint verification bytes;88 imports;data/layout/history/image gates open')
if __name__=='__main__':audit()
