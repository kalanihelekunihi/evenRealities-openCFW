#!/usr/bin/env python3
"""Authenticate shared mode/pair bodies, native overlap and source control graph."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-mode';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_gxt310_mode.o'
 assert r['comparisons']==113032 and r['counts']=={'shared':56320,'channel0':5280,'channel2':5280,'enable':46080,'disable':72} and r['callback_observations_per_side']==341482 and r['write_calls_per_side']==66880 and r['trace_sha256']=='09aa4afb6d99fabad31c7a091d8e439fd9d2c89eb00b7d049722a46fde85c03a'
 for flag in ['full_four_byte_config_word_checked','zero_enabled_sets_low_byte_bit0_only','any_nonzero_write_result_is_success','write_buffer_mutated_by_fixture','pair_always_calls_both_channels_before_logging','pair_result_is_raw_bitwise_and','disable_raw_r0_matches_last_channel_fixture','full_width_statuses_and_modes_and_all_byte_addresses','raw_r0_callee_integer_stack_full_observed_nonstack_ram_and_typed_callback_args_order_checked','private_config_pointer_normalized','write_logging_and_pair_channel_providers_are_fixtures','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['whole_startup_graph_executed'] and not r['physical_sensor_verified'] and not r['instruction_identity'] and not r['full_raw_abi_verified'] and r['source_data_bytes']==308
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_gxt310_mode.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app)
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 assert report['units'][0]['source_sha256']==sha(ROOT/report['units'][0]['source']) and not report['application_linked'] and not report['instruction_identity']
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 regions=[(0x50f88,18),(0x50f9c,138),(0x6f648,106),(0x6f804,8),(0x6f81e,8),(0x6f6b4,4),(0x6f6b8,64),(0x6f6f8,8),(0x6f700,56),(0x51028,8),(0x51030,44),(0x5105c,40),(0x51084,44),(0x510b0,40)]
 for a,n in regions:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a,n in [(0x50f88,124),(0x50f9c,138),(0x6f648,124),(0x6f804,8),(0x6f81e,8)]:
  rea=read(OUT/f'rea-{a:x}.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));body=rea['normalized_result']['body'];assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and body['total_bytes']==n
  if a in [0x50f88,0x6f648]:assert body['ranges']==[{'start':'0x50f88','end':'0x50f99'},{'start':'0x6f648','end':'0x6f6b1'}]
  else:assert body['ranges']==[{'start':hex(a),'end':hex(a+n-1)}]
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['gross_row_bytes']==384 and e['unique_native_bytes']==278 and e['power_down_row_bytes']==124 and e['shared_mode_bytes_counted_once'] and not e['locked_ownership_changed'] and not e['whole_image_identity'] and not e['upstream_vendor_implementation_claim']
 probes=read(OUT/e['compiler_frame_probes']);assert e['compiler_frame_probes_sha256']==sha(OUT/e['compiler_frame_probes']) and probes['baseline_report_sha256']==sha(rp) and len(probes['trials'])==3
 for trial in probes['trials']:assert sha(OUT/trial['saved_object'])==trial['object_sha256'] and trial['source_sha256']==report['units'][0]['source_sha256']
 assert not e['sampled_native_write_read_pointer_alias'] and e['sampled_source_write_read_pointer_alias'] and not e['future_null_write_after_stack_reuse_verified']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_rows']==[x for x in rows if x['image']=='application' and x['entry'] in ['0x00050f88','0x00050f9c','0x0006f648','0x0006f804','0x0006f81e']]
 from audit_source_frontier import section_bytes
 REGIONS=[('word',0x6f6b4,4),('error_ring',0x6f6b8,64),('bounds',0x6f6f8,8),('error_sdk',0x6f700,56),('pair_bounds',0x51028,8),('pair0_ring',0x51030,44),('pair0_sdk',0x5105c,40),('pair2_ring',0x51084,44),('pair2_sdk',0x510b0,40)]
 for name,a,n in REGIONS:assert section_bytes(obj,'.r1.gxt.mode.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 for name in ['r1_gxt310_mode_channel0','r1_gxt310_mode_channel2']:
  relocs=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_THM_JUMP24)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.text.'+name,str(obj)],text=True),re.M);assert relocs==[('00000004','R_ARM_THM_JUMP24','r1_gxt310_switch_mode_native')]
 bp=BASE/'native-gxt310-mode-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-gxt310-mode-runtime.o') and bundle['control_object_sha256']==sha(bp.parent/'gxt-control-source.o') and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==63 and len(bundle['control_undefined_symbols'])==10 and not bundle['whole_startup_graph_executed'] and not bundle['physical_sensor_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-gxt310-mode-runtime.o')[0]==bundle['undefined_symbols'] and undefined_symbols(bp.parent/'gxt-control-source.o')[0]==bundle['control_undefined_symbols'] and not any(n.startswith('r1_gxt310_') for n in bundle['undefined_symbols'])
 g=read(OUT/'graph-verification.json');assert g['comparisons']==16572 and g['callback_observations_per_side']==495412 and g['trace_sha256']=='6bf4c8718ba9efc38840e5b2d0b47168b25b46de0c294d8aa231f73fa956a847' and g['runtime_report_sha256']==sha(bp) and g['object_sha256']==bundle['control_object_sha256'] and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_gxt310_control_graph.py') and g['layout_sha256']==sha(ROOT/g['layout']) and g['application_sha256']==sha(app)
 for flag in ['actual_source_cache_selfcheck_bus_requests_mode_pair_controls_channel_veneers_and_ids','only_registry_and_logging_are_named_fixtures','all_four_mode_writes_both_reads_and_cleanup_order_checked','full_four_byte_mode_words_and_zero_read_words_checked','cold_c_state_used','registry_null_device_status_fixture_is_one','raw_r0_callee_integer_stack_and_typed_callback_args_checked','full_observed_nonstack_ram_compared_with_two_pointer_words_normalized','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert g[flag],flag
 assert g['normalized_pointer_fields']==['state+8 write_pointer','state+16 read_pointer'] and not g['raw_persistent_pointer_values_equal'] and not g['whole_startup_graph_executed'] and not g['physical_sensor_verified'] and not g['instruction_identity'] and not g['full_raw_abi_verified'] and g['source_selected_strings_and_name_bytes']==388 and g['source_state_bytes']==24
 assert len(g['raw_persistent_pointer_counterexamples'])==3
 for example in g['raw_persistent_pointer_counterexamples']:assert example['native_write_read_pointers']!=example['source_write_read_pointers'] and all(0x2003e000<=p<0x2003f000 for p in example['native_write_read_pointers']+example['source_write_read_pointers'])
 old=read(OUT/e['initial_normalized_graph_receipt']);assert e['initial_normalized_graph_receipt_sha256']==sha(OUT/e['initial_normalized_graph_receipt']) and e['initial_normalized_graph_driver_sha256']==sha(OUT/e['initial_normalized_graph_driver']) and old['object_sha256']==g['object_sha256'] and old['trace_sha256']==g['trace_sha256'] and not old['raw_persistent_pointer_values_equal']
 print('GXT mode authenticated:113032 direct cases +16572 source control workflows;63 startup imports;two raw request-pointer differences and hardware/ABI/image gates remain')
if __name__=='__main__':audit()
