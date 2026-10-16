#!/usr/bin/env python3
"""Authenticate native YHM startup/GXT check contracts and source integration."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-checks';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_device_checks.o'
 assert r['callback_observations_per_side']==1099978 and r['delay_calls_per_side']==448400 and r['write_calls_per_side']==44840 and r['trace_sha256']=='2ee70f6bc04b013aede5485051e3154ba3fc416a4a3000898e9f673e37e73278'
 assert r['comparisons']==110424 and r['counts']=={'yhm':40448,'void_adapter':3840,'gxt':66136}
 for flag in ['native_yhm_writes_return_values_ignored','native_success_delay_fifty_calls_64000','failed_chip_has_no_writes_or_delay','all_8bit_chip_ids_and_selected_high_values','all_8bit_gxt_id_pairs_and_selected_high_values','gxt_always_acquires_enables_reads_both_disables_releases','write_buffer_reused_and_mutated_by_fixture','normalized_write_pointer_private_frame_gate','callback_arguments_order_status_state_full_ram_raw_r0_stack_and_callee_integer_checked','source_void_adapter_raw_r0_sampled','all_leaf_providers_are_named_fixtures','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled','delay_pointer_is_source_relocation']:assert r[flag],flag
 assert not r['actual_delay_body_executed'] and not r['whole_device_graph_executed'] and not r['instruction_identity'] and not r['full_raw_abi_verified'] and not r['physical_hardware_verified'] and r['source_constant_data_bytes']==120
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_device_checks.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app)
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 assert report['units'][0]['source_sha256']==sha(ROOT/report['units'][0]['source']) and not report['application_linked'] and not report['instruction_identity']
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 for a,n in [(0x3510c,224),(0x351ec,8),(0x351f4,32),(0x35214,24),(0x3522c,32),(0x3524c,24),(0x35264,4),(0x50ecc,46)]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a in [0x3510c,0x50ecc]:
  rea=read(OUT/f'rea-{a:x}.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['error']['code']=='invalid_request' and 'No procedure exists' in str(rea) and '92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' in str(rea)
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['native_yhm_bytes']==224 and e['native_gxt_bytes']==46 and e['source_data_bytes']==120 and e['source_delay_pointer_relocation_bytes']==4 and not e['locked_ownership_changed'] and not e['whole_image_identity'] and not e['upstream_vendor_implementation_claim']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_rows']==[x for x in rows if x['image']=='application' and x['entry'] in ['0x0003510c','0x00050ecc']]
 assert e['old_generic_configure_sha256']==sha(ROOT/e['old_generic_configure_source']) and e['old_generic_not_used_for_native_provider'] and 'return ok ? 0u : 5u;' in (ROOT/e['old_generic_configure_source']).read_text()
 from audit_source_frontier import section_bytes
 for name,a,n in [('bounds',0x351ec,8),('error_ring',0x351f4,32),('error_sdk',0x35214,24),('success_ring',0x3522c,32),('success_sdk',0x3524c,24)]:assert section_bytes(obj,'.r1.device.checks.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 relocs=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_ABS32)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.r1.device.checks.delay',str(obj)],text=True),re.M);assert relocs==[('00000000','R_ARM_ABS32','r1_rtt_delay_cycles')]
 bp=BASE/'native-device-checks-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-device-checks-runtime.o') and bundle['selected_yhm_object_sha256']==sha(bp.parent/'yhm-write-discovery.o') and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==71 and not bundle['full_provider_graph_execution_verified'] and not bundle['physical_sensor_or_delay_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-device-checks-runtime.o')[0]==bundle['undefined_symbols'] and not set(['r1_gxt310_self_check','r1_device_preinitialize_3510c','r1_yhm_register_write_native','r1_yhm_device_handles_initialize','r1_rtt_delay_cycles'])&set(bundle['undefined_symbols'])
 print('Native YHM/GXT startup authenticated:110424 cases; source write/discovery/state/delay linked;71 transitive imports and raw ABI/hardware/image gates remain')
if __name__=='__main__':audit()
