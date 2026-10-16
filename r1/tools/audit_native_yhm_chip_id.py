#!/usr/bin/env python3
"""Authenticate native YHM chip-ID byte lifetime, constants and source linkage."""
import csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-yhm-chip-id';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_yhm_chip_id.o'
 assert r['callback_observations_per_side']==466560 and r['trace_sha256']=='78ede87d42d0f4d99de3302d2c78b885bff9f9d5e200a529d84cd9a0df084f6f'
 assert r['comparisons']==98304
 for flag in ['read_register8_length1_initial_zero','read_status_ignored_and_no_write_result_supported','all_byte_ids_and_mode_triples','seeded_full_width_modes','callback_mutations_of_scoped_read_byte','initial_id_selects_log_strings_late_byte_is_returned','raw_r0_stack_callee_integer_full_nonstack_ram_and_callback_order_args_checked','read_pointer_normalized_private_frame_gate','read_and_logging_bodies_are_named_fixtures','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['actual_source_transport_executed'] and not r['whole_startup_graph_executed'] and not r['instruction_identity'] and not r['full_raw_abi_verified'] and not r['physical_hardware_verified'] and r['source_data_bytes']==120
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_chip_id.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app)
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 assert report['units'][0]['source_sha256']==sha(ROOT/report['units'][0]['source']) and not report['application_linked'] and not report['instruction_identity']
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x3530c,134),(0x35394,8),(0x3539c,32),(0x353bc,24),(0x353d4,32),(0x353f4,24)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 rea=read(OUT/'rea-3530c.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['error']['code']=='invalid_request' and 'No procedure exists' in str(rea) and '92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' in str(rea)
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['native_body_bytes']==134 and e['source_data_bytes']==120 and not e['locked_ownership_changed'] and not e['whole_image_identity'] and not e['upstream_vendor_implementation_claim'] and e['read_status_ignored'] and e['unwritten_byte_remains_zero'] and e['log_selection_snapshots_initial_read_byte'] and e['return_reloads_live_byte_after_callbacks'] and e['source_transport_linked_not_executed_here']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_row']==next(x for x in rows if x['image']=='application' and x['entry']=='0x0003530c')
 from audit_source_frontier import section_bytes
 for name,a,n in [('bounds',0x35394,8),('success_ring',0x3539c,32),('success_sdk',0x353bc,24),('error_ring',0x353d4,32),('error_sdk',0x353f4,24)]:assert section_bytes(obj,'.r1.yhm.chip.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 bp=BASE/'native-yhm-chip-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-yhm-chip-runtime.o') and bundle['selected_yhm_object_sha256']==sha(bp.parent/'yhm-read-write-discovery.o') and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==70 and not bundle['full_provider_graph_execution_verified'] and not bundle['physical_sensor_or_delay_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-yhm-chip-runtime.o')[0]==bundle['undefined_symbols'] and not set(['r1_gxt310_self_check','r1_device_preinitialize_3510c','r1_yhm_register_write_native','r1_yhm_device_handles_initialize','r1_rtt_delay_cycles','r1_yhm_chip_id_native','r1_yhm_register_read_native'])&set(bundle['undefined_symbols'])
 print('Native YHM chip ID authenticated:98304 cases; source read/write/discovery/state/delay linked;70 transitive startup imports and hardware/ABI/image gates remain')
if __name__=='__main__':audit()
