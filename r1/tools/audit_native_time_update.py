#!/usr/bin/env python3
"""Authenticate native clock update/flag/snapshot state and callback contracts."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-time-update';b=json.loads((out/'report.json').read_text());v=json.loads((out/'verification.json').read_text());c=json.loads((out/'contracts.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();assert sha(app)==v['application_sha256']==c['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for unit in b['units']:assert unit['compiled'] and sha(ROOT/unit['source'])==unit['source_sha256']==c['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']==v['object_sha256']
 assert sha(BASE/'i2c5/stock-analysis-exec.elf')==c['analysis_elf_sha256'] and sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')==c['frozen_pseudocode_sha256'] and sha(ROOT/'r1/tools/recover_native_time_update.py')==c['generator_sha256']
 parent=BASE/'native-activity-storage';po=parent/'native-activity-storage-runtime.o';clone=out/'parent-calendar-symbols.o';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(po)==b['parent_object_sha256'] and sha(clone)==b['parent_symbol_clone_sha256'] and allocated_sections(po)==allocated_sections(clone)
 old=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(po)],text=True).splitlines());new=Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(clone)],text=True).splitlines());row=('00000000','00000058','T','r1_clock_backend_snapshot');assert old[row]==1 and new[(row[0],row[1],'W',row[3])]==1;del old[row];del new[(row[0],row[1],'W',row[3])];assert old==new and b['replacement_symbols']==['r1_clock_backend_snapshot'] and not b['exposed_existing_config_symbols'] and b['parent_allocated_sections_unchanged'] and b['parent_other_symbols_unchanged']
 config=out/'shared-time-config.o';assert sha(config)==b['shared_config_object_sha256']==v['shared_config_object_sha256'] and sum(x[2] for x in allocated_sections(config).values())==b['shared_existing_config_bytes']==56 and b['new_ram_state_bytes']==0
 for filename,hk,uk in [('native-time-update-runtime.o','linked_sha256','undefined_symbols'),('time-update-source.o','graph_object_sha256','graph_undefined_symbols')]:assert sha(out/filename)==b[hk] and undefined_symbols(out/filename)[0]==b[uk]
 assert len(b['undefined_symbols'])==79 and b['closed_parent_imports']==['r1_event_service_0008aea4','r1_event_service_0008aeb0'] and not b['newly_exposed_imports']
 assert sha(out/'report.json')==v['report_sha256'] and sha(ROOT/'r1/tools/verify_native_time_update.py')==v['driver_sha256'] and v['comparisons']==17411 and v['counts']=={'setter':256,'snapshot':7170,'update':9985,'faults':3,'get_calls':4878,'update_calls':5472,'clears':4368} and v['trace_sha256']=='d3526395f81675a86076f4af8f456cd0fdf100828155852e5be853992090f6ee'
 sections=allocated_sections(out/'native_time_update.o')
 for x in c['bodies']:
  assert sum(i['size'] for i in x['instructions'])==x['code_bytes'] and sections['.text.'+x['symbol']][2]==x['source_span_bytes'] and sha(out/('disassembly-'+x['address'][2:]+'.txt'))==x['disassembly_sha256']
  r=json.loads((out/('rea-'+x['address'][2:]+'.json')).read_text())['structuredContent'];n=r['normalized_result'];a=int(x['address'],16)-0x27000;assert r['subject']['digest']['sha256']==c['analysis_elf_sha256'] and n['complete'] and n['returned_bytes']==x['source_span_bytes'] and bytes.fromhex(n['bytes_hex'])==raw[a:a+x['source_span_bytes']]
 assert c['native_code_bytes']==b['native_body_bytes']==176 and c['native_span_bytes']==b['native_source_span_bytes']==192 and c['new_ram_state_bytes']==0 and c['shared_config']=={'r1_time_state':{'address':'0x20016ac4','size':32},'r1_time_registration':{'address':'0x20006820','size':24}}
 for x in v['exact_spans']:
  a=int(x['address'],16)-0x27000;assert hashlib.sha256(raw[a:a+x['size']]).hexdigest()==x['sha256']
 assert len(v['exact_spans'])==3 and sum(x['size'] for x in v['exact_spans'])==v['exact_bytes']==192 and v['actual_flag_update_and_snapshot_execute'] and v['backend_callbacks_and_memclr_are_fixtures'] and v['independent_state_cache_and_callback_contract_oracle'] and v['all_capture_and_snapshot_flag_bytes_checked'] and v['fresh_stack_snapshot_and_context_after_get_mutation_checked']
 assert not v['full_private_history_or_raw_abi_verified'] and not v['whole_image_complete'] and not v['hardware_write_executed']
 print('Time update:17411 comparisons;56 existing state bytes;192 exact verification bytes;79 imports;backend/memclear/caller/layout/image gates open')
if __name__=='__main__':audit()
