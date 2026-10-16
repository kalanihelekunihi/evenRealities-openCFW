#!/usr/bin/env python3
"""Bind upstream DFU entry, recovered shared tail, native tools and startup link."""
import csv,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-dfu-svci-init';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes()
 assert r['comparisons']==10896 and r['counts']=={'entry':3216,'restore':7680} and r['callback_observations_per_side']==79988 and r['supervisor_calls_per_side']=={'0':2136,'19':9636} and r['trace_sha256']=='c723d5d428a5b2a001e7085d69733216bbdd1718245fe45d4871fd6042315f07'
 for flag in ['upstream_entry_and_source_restore_executed','actual_svc0_bridge_executed','supervisor_behavior_is_fixture','vector_set_and_logging_bodies_are_named_fixtures','all_entry_raw_r0_compared','callee_integer_stack_and_full_nonstack_ram_checked','all_three_mode_values_exhaustive_per_log_group','independent_seeded_six_mode_queues','early_error_and_state_mutation_paths','source_data_at_native_verification_addresses','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['instruction_identity'] and not r['full_raw_abi_verified'] and not r['physical_svc_verified'] and r['source_constant_data_bytes']==216 and r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_dfu_svci_init.py') and r['report_sha256']==sha(rp) and r['object_sha256']==report['linked_sha256']==sha(OUT/'native-dfu-svci-init.o') and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app)
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 sdk=read(BASE/'application-sdk/report.json');u=next(x for x in sdk['units'] if 'ble_dfu_buttonless_async_svci_init' in x.get('defined',[]));assert report['provider_report_sha256']==sha(BASE/'application-sdk/report.json') and report['provider_object_sha256']==u['object_sha256']==sha(Path(u['command'][-1])) and report['sdk_archive_sha256']==sdk['sdk_archive_sha256'] and report['compiler_adaptations']==sdk['compiler_adaptations']
 assert report['selected_object_sha256']==sha(OUT/'nordic-dfu-init.o') and report['upstream_entry_source_unmodified'] and not report['image_linked'] and not report['instruction_identity']
 for unit in report['units']:assert sha(ROOT/unit['source'])==unit['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x52018,32),(0x52038,4),(0x7876c,130),(0x787f0,4),(0x787f4,48),(0x78824,8),(0x7882c,44),(0x78858,60),(0x78894,52)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a in [0x52018,0x7876c]:
  rea=read(OUT/f'rea-{a:x}.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea['normalized_result']['body']['ranges']==[{'start':'0x52018','end':'0x52037'},{'start':'0x7876c','end':'0x787ed'}] and rea['normalized_result']['body']['total_bytes']==162
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['native_body_bytes']==162 and e['source_data_bytes']==216 and e['source_async_state_bytes']==12 and not e['locked_ownership_changed'] and not e['whole_image_identity']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_row']==next(x for x in rows if x['image']=='application' and x['entry']=='0x00052018') and e['ownership_row']['size']=='162'
 from audit_source_frontier import section_bytes
 REGIONS=[('app_start',0x787f0,4),('info_ring',0x787f4,48),('bounds',0x78824,8),('info_sdk',0x7882c,44),('error_ring',0x78858,60),('error_sdk',0x78894,52)]
 for name,a,n in REGIONS:assert section_bytes(OUT/'native_dfu_vector_restore.o','.r1.dfu.restore.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert section_bytes(OUT/'nordic-dfu-init.o','.text.svci_nrf_dfu_set_adv_name_svci_async_init',executable=True).hex()==report['svc_bridge_instruction_bytes']=='4ff0030c00df7047'
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(OUT/'native-dfu-svci-init.o')[0]==report['undefined_symbols']
 bp=BASE/'native-dfu-startup-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-dfu-startup-runtime.o') and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==68 and 'nrf_dfu_svci_vector_table_set' in bundle['undefined_symbols'] and not bundle['full_provider_execution_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 assert undefined_symbols(bp.parent/'native-dfu-startup-runtime.o')[0]==bundle['undefined_symbols']
 print('DFU entry/shared restore authenticated:10896 cases; all13 direct app imports source-linked;68 transitive imports and SVC/raw ABI/image gates remain')
if __name__=='__main__':audit()
