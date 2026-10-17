#!/usr/bin/env python3
"""Authenticate source calendar frames, existing config ownership and compositions."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-calendar-frames';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());cv=json.loads((out/'storage-composed-verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==cv['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']==cv['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_calendar_frames.py')==c['generator_sha256']
 parent=BASE/'native-health-average';po=parent/'native-health-average-runtime.o';clone=out/'parent-calendar-symbols.o';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(po)==b['parent_object_sha256'] and sha(clone)==b['parent_symbol_clone_sha256'] and allocated_sections(po)==allocated_sections(clone)
 old=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(po)],text=True).splitlines());new=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(clone)],text=True).splitlines())
 assert b['replacement_symbols']==['r1_time_utc_offset_get','time_calendar_utc_to_calendar','time_calendar_unix_to_broken_down'] and b['exposed_existing_config_symbols']==['unix_to_broken_down_fallback','month_days_forward']
 for n,size,ot,nt in [(n,s,'T','W') for n,s in zip(b['replacement_symbols'],[14,132,388])]+[('unix_to_broken_down_fallback',36,'b','B'),('month_days_forward',24,'r','R')]:
  row=('00000000','%08x'%size,ot,n);assert old[row]==1 and new[(row[0],row[1],nt,n)]==1;del old[row];del new[(row[0],row[1],nt,n)]
 assert old==new and b['parent_allocated_sections_unchanged'] and b['parent_other_symbols_unchanged']
 config=out/'shared-calendar-config.o';assert sha(config)==b['shared_config_object_sha256']==v['shared_config_object_sha256']==cv['shared_config_object_sha256'] and sum(x[2] for x in allocated_sections(config).values())==b['shared_existing_config_bytes']==92 and b['new_ram_state_bytes']==0
 assert sha(parent/'native_health_average.o')==cv['average_object_sha256'] and sha(BASE/'native-health-sample-storage/native_health_sample_storage.o')==cv['storage_object_sha256']
 for filename,hk,uk in [('native-calendar-frames-runtime.o','linked_sha256','undefined_symbols'),('calendar-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==82 and not b['closed_parent_imports'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256']==cv['report_sha256'] and sha(ROOT/'r1/tools/verify_native_calendar_frames.py')==v['driver_sha256'] and sha(ROOT/'r1/tools/verify_native_calendar_storage_composed.py')==cv['driver_sha256']
 assert v['comparisons']==89407 and v['counts']=={'offset':65536,'unix':5343,'utc':18528,'faults':6} and v['trace_sha256']=='4f67b1ef757739fb45dd8ce76212e3dbb08d4d10a469c9e2449635c86c086dc4'
 assert cv['comparisons']==5952 and cv['counts']=={'single_storage_calls':4800,'alias_sequence_calls':1152} and cv['sequences']==5184 and cv['trace_sha256']=='165034bfb2354b89adab2161f4fe70fd9118be6c18497472e0c64a566c474c6e'
 sections=allocated_sections(out/'native_calendar_frames.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(out/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  r=json.loads((out/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(n['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==310 and c['native_span_bytes']==b['native_source_span_bytes']==328 and c['new_ram_state_bytes']==0
 assert c['shared_config']=={'r1_time_state':{'address':'0x20016ac4','size':32},'unix_to_broken_down_fallback':{'address':'0x20016ae4','size':36},'month_days_forward':{'address':'0x99c5c','size':24}}
 for receipt,count,size in [(v,4,352),(cv,12,2683)]:
  assert len(receipt['exact_spans'])==count and sum(x['size'] for x in receipt['exact_spans'])==receipt['exact_bytes']==size
  for x in receipt['exact_spans']:
   a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 provenance=json.loads((out/'provider-provenance.json').read_text());assert provenance['new_bodies_are_owner_authorized_native_frames'] and not provenance['new_vendor_or_upstream_attribution_claimed'] and provenance['original_month_table_and_fallback_owners_reused']
 for p,h in provenance['comparison_only_existing_provider_files'].items():assert sha(ROOT/p)==h,p
 assert v['all_65536_offset_words_checked'] and v['datetime_and_native_sequential_alias_oracle'] and v['actual_calendar_chain_executes_without_provider_fixtures'] and v['shared_config_native_placements_are_verification_bindings']
 assert cv['actual_storage_average_hour_offset_calendar_unix_source_chain_executes'] and cv['hrv_stress_hrv_shared_row5_sequences_execute'] and cv['independent_coupled_cache_fp_alias_and_mutation_oracle'] and not cv['calendar_provider_is_fixture'] and cv['timezone_packet_changes_and_logging_are_controlled_fixtures']
 for receipt in [v,cv]:assert not receipt['full_private_history_or_raw_abi_verified'] and not receipt['whole_image_complete'] and not receipt['hardware_write_executed']
 print('Calendar frames:89407 direct+5952 source-storage comparisons;92 config bytes reused;328 new/2683 joint verification bytes;82 imports;runtime/layout/history/image gates open')
if __name__=='__main__':audit()
