#!/usr/bin/env python3
"""Authenticate GXT reader/veneers and actual source self-check subgraph."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-id';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_gxt310_id.o'
 assert r['comparisons']==137536 and r['counts']=={'shared':123136,'channel0':7200,'channel2':7200} and r['callback_observations_per_side']==650968 and r['trace_sha256']=='69ca27e0c6de1064671b0037693a9a07412d57e42b20e98d48a830e35ef4b88f'
 for flag in ['all_65536_read_words','shared_and_both_channel_veneers_executed','read_reg3_length2_initial_zero','entire_private_word_four_bytes_initial_zero','read_result_ignored_and_no_write_result_supported','full_width_addresses_and_seeded_modes','scoped_callback_buffer_mutations','log_value_is_initial_big_endian_16bit_snapshot','ring_fifth_stack_argument_checked','return_reloads_late_first_byte','raw_r0_stack_callee_integer_full_observed_nonstack_ram_and_callback_args_order_checked','private_read_pointer_normalized','read_and_logging_bodies_are_fixtures','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['actual_source_read_transport_executed'] and not r['whole_startup_graph_executed'] and not r['instruction_identity'] and not r['full_raw_abi_verified'] and not r['physical_hardware_verified'] and r['source_data_bytes']==100
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_gxt310_id.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app)
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 assert report['units'][0]['source_sha256']==sha(ROOT/report['units'][0]['source']) and not report['application_linked'] and not report['instruction_identity']
 for group in ['ghidra','rea','boundary_observations']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x6f53c,96),(0x6f812,6),(0x6f82c,6),(0x6f59c,48),(0x6f5cc,8),(0x6f5d4,44)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a in [0x6f53c,0x6f812,0x6f82c]:
  rea=read(OUT/f'rea-{a:x}.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'))
  if a==0x6f53c:assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea['normalized_result']['body']['ranges']==[{'start':'0x6f53c','end':'0x6f59b'}] and rea['normalized_result']['body']['total_bytes']==96
  else:assert rea['error']['code']=='invalid_request' and 'No procedure exists' in str(rea)
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['total_native_bytes']==108 and e['source_data_bytes']==100 and e['selected_selfcheck_graph_data_bytes']==92 and e['folded_bounds_not_selected_graph_data'] and e['native_private_zero_word_bytes']==e['source_private_zero_word_bytes']==4 and e['typed_source_requested_buffer_bytes']==2 and e['power_down_row_not_promoted'] and not e['locked_ownership_changed'] and not e['whole_image_identity'] and not e['upstream_vendor_implementation_claim']
 history=read(OUT/e['initial_two_byte_candidate_manifest']);assert e['initial_two_byte_candidate_manifest_sha256']==sha(OUT/e['initial_two_byte_candidate_manifest']) and history['status']=='superseded-before-admission'
 for old in history['files'].values():assert sha(OUT/'initial-two-byte-candidate'/old['snapshot'])==old['sha256']
 for name in e['boundary_observations']:
  boundary=read(OUT/name);boundary=boundary.get('structuredContent') or json.loads(next(x['text'] for x in boundary['content'] if x['type']=='text'));assert boundary['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and boundary['normalized_result']['body']['ranges']==[{'start':'0x50f88','end':'0x50f99'},{'start':'0x6f648','end':'0x6f6b1'}] and boundary['normalized_result']['body']['total_bytes']==124
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_rows']==[x for x in rows if x['image']=='application' and x['entry'] in ['0x0006f53c','0x0006f812','0x0006f82c']]
 from audit_source_frontier import section_bytes
 for name,a,n in [('ring',0x6f59c,48),('bounds',0x6f5cc,8),('sdk',0x6f5d4,44)]:assert section_bytes(obj,'.r1.gxt.id.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 bp=BASE/'native-gxt310-id-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-gxt310-id-runtime.o') and bundle['selfcheck_object_sha256']==sha(bp.parent/'gxt-selfcheck-source.o') and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==69 and len(bundle['selfcheck_undefined_symbols'])==8 and not bundle['whole_startup_graph_executed'] and not bundle['physical_sensor_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-gxt310-id-runtime.o')[0]==bundle['undefined_symbols'] and undefined_symbols(bp.parent/'gxt-selfcheck-source.o')[0]==bundle['selfcheck_undefined_symbols'] and 'r1_gxt310_register_read_native' in bundle['undefined_symbols'] and not {'r1_gxt310_chip_id_channel0','r1_gxt310_chip_id_channel2'}&set(bundle['undefined_symbols'])
 for name in ['r1_gxt310_chip_id_channel0','r1_gxt310_chip_id_channel2']:
  relocs=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_THM_JUMP24)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.text.'+name,str(obj)],text=True),re.M);assert relocs==[('00000002','R_ARM_THM_JUMP24','r1_gxt310_chip_id_native')]
 g=read(OUT/'graph-verification.json');assert g['callback_observations_per_side']==591498 and g['trace_sha256']=='cd73aa0ccc79d82eb371fd801f3bb80d986342587d481716ac9bc34419a99c11'
 assert g['comparisons']==44096 and g['runtime_report_sha256']==sha(bp) and g['object_sha256']==bundle['selfcheck_object_sha256'] and g['driver_sha256']==sha(ROOT/'r1/tools/verify_native_gxt310_id_graph.py') and g['imported_driver_sha256']==r['driver_sha256'] and g['layout_sha256']==sha(ROOT/g['layout']) and g['application_sha256']==sha(app)
 for flag in ['actual_source_selfcheck_both_veneers_and_shared_reader','id_providers_are_source_not_fixtures','entire_private_word_four_bytes_initial_zero','folded_log_bounds_not_selected_graph_data','bus_enable_disable_read_and_logging_are_fixtures','initial_id_log_snapshot_and_late_return_mutations','cleanup_order_and_both_reads_checked','raw_r0_stack_callee_integer_full_observed_nonstack_ram_and_typed_callback_args_checked','read_pointers_private_frame_normalized','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert g[flag],flag
 assert g['selected_graph_constant_data_bytes']==92 and not g['whole_startup_graph_executed'] and not g['physical_sensor_verified'] and not g['instruction_identity']
 print('GXT ID authenticated:137536 direct cases +44096 actual source self-check workflows;69 startup imports and leaf/hardware/private ABI/image gates remain')
if __name__=='__main__':audit()
