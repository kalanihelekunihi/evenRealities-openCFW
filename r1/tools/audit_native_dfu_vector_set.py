#!/usr/bin/env python3
"""Bind upstream vector fallback, R1 log macros, DFU graph and native evidence."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-dfu-vector-set';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes()
 assert r['callback_observations_per_side']==703230 and r['supervisor_calls_per_side']=={'0':5352,'19':70764} and r['trace_sha256']=='17e1775e86398b6bdf111a6fdf9b2598af6d807b1016d4f61d1ac3c90377492c'
 assert r['comparisons']==77568 and r['counts']=={'entry':16128,'set':61440}
 for flag in ['upstream_setter_entry_and_source_restore_executed','actual_svc0_and_svc19_bridges_executed','supervisor_behavior_is_fixture','logging_bodies_are_named_fixtures','vector_set_provider_is_source_not_fixture','all_entry_raw_r0_compared','callee_integer_stack_and_full_nonstack_ram_checked','mode_queues_and_early_errors_exercised','boot_mbr_precedence_uicr_fallback_and_both_missing','boot_zero_one_unaligned_and_high_bit_values','boot_read_order_and_inputs_unchanged','source_data_at_native_verification_addresses','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['instruction_identity'] and not r['full_raw_abi_verified'] and not r['physical_svc_verified'] and r['source_selected_constant_data_bytes']==480 and r['setter_source_data_bytes']==272 and r['setter_selected_source_data_bytes']==264
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_dfu_vector_set.py') and r['report_sha256']==sha(rp) and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app)
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 sdk=read(BASE/'application-sdk/report.json');u=next(x for x in sdk['units'] if x['source'].endswith('/nrf_dfu_svci.c'));assert report['provider_report_sha256']==sha(BASE/'application-sdk/report.json') and report['sdk_archive_sha256']==sdk['sdk_archive_sha256'] and report['upstream_source_sha256']==u['source_sha256']==sha(ROOT/u['source']) and report['upstream_source_unmodified'] and not report['image_linked'] and not report['instruction_identity']
 for unit in report['units']:assert sha(ROOT/unit['source'])==unit['source_sha256'] and sha(Path(unit['command'][-1]))==unit['object_sha256']
 assert report['linked_sha256']==sha(OUT/'native-dfu-vector-set.o')
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x78590,202),(0x7865c,8),(0x78664,52),(0x78698,44),(0x786c4,60),(0x78700,52),(0x78734,32),(0x78754,24)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 rea=read(OUT/'rea-78590.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea['normalized_result']['body']['ranges']==[{'start':'0x78590','end':'0x78659'}] and rea['normalized_result']['body']['total_bytes']==202
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and not e['locked_ownership_changed'] and not e['whole_image_identity']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_row']==next(x for x in rows if x['image']=='application' and x['entry']=='0x00078590') and e['ownership_row']['size']=='202'
 from audit_source_frontier import section_bytes
 for section,a,n in [('ring.57',0x78664,52),('sdk.57',0x78698,44),('ring.61',0x786c4,60),('sdk.61',0x78700,52),('ring.68',0x78734,32),('sdk.68',0x78754,24)]:assert section_bytes(OUT/'native-dfu-vector-set.o','.r1.dfu.vector.'+section,executable=False)==raw[a-0x27000:a-0x27000+n]
 assert section_bytes(OUT/'log_port.o','.r1.dfu.vector.bounds',executable=False)==raw[0x7865c-0x27000:0x78664-0x27000]
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(OUT/'native-dfu-vector-set.o')[0]==report['undefined_symbols']
 bp=BASE/'native-dfu-vector-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-vector-startup-runtime.o') and bundle['dfu_runtime_sha256']==r['object_sha256']==sha(bp.parent/'native-dfu-vector-runtime.o') and r['runtime_report_sha256']==sha(bp) and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==67 and 'nrf_dfu_svci_vector_table_set' not in bundle['undefined_symbols'] and not bundle['full_provider_graph_execution_verified'] and not bundle['physical_supervisor_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 assert undefined_symbols(bp.parent/'native-vector-startup-runtime.o')[0]==bundle['undefined_symbols'] and undefined_symbols(bp.parent/'native-dfu-vector-runtime.o')[0]==bundle['dfu_undefined_symbols']==report['undefined_symbols']
 assert e['graph_setter_provider_is_actual_source'] and e['physical_supervisor_is_fixture'] and e['source_log_bounds_folded_not_selected_layout'] and not e['whole_startup_graph_executed']
 print('Upstream DFU vector setup and source DFU graph authenticated:77568 cases;67 startup transitive imports and physical SVC/raw ABI/image gates remain')
if __name__=='__main__':audit()
