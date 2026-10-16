#!/usr/bin/env python3
"""Audit device/reset startup contracts, source data and partial integration."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-device-reset-startup';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_device_reset_startup.o'
 assert r['comparisons']==16377 and r['counts']=={'module':4968,'tail':4968,'rtc':35,'thunk':35,'reset':6336,'noop':35} and r['callback_observations_per_side']==85473 and r['trace_sha256']=='3d9598f50cf41bc3652bba6e384650e2b1e636d653384a19bca410b64d38f28f'
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_device_reset_startup.py') and r['application_sha256']==sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a' and r['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout']) and r['data_regions_sha256']==sha(ROOT/r['data_regions'])
 assert not r['module_r0_excluded_from_typed_equivalence'] and r['raw_module_r0_equal'] and r['all_entry_raw_r0_compared'] and not r['runtime_no_unresolved'] and not r['provider_source_integration_verified'] and not r['instruction_identity']
 for flag in ['typed_calls_state_writes_full_ram_return_stack_and_callee_integer_checked','leaf_provider_bodies_are_named_fixtures','source_module_shared_tail_rtc_thunk_reset_and_noop','source_noop_original_address_only_native_range_execution_allowed','selected_six_value_mode_queues','rtc_handle_reload_after_open','selfcheck_state_byte_rmw_after_callback','reset_snapshot_preserved_across_provider_mutation','reset_one_hot_flags_and_seeded_values','unicorn_memory_write_hooks_disabled']:assert r[flag]
 for path,h in report['inputs'].items():assert sha(ROOT/path)==h,path
 for group in ['ghidra','rea']:
  for path,h in e[group].items():assert sha(OUT/path)==h,path
 regions=read(ROOT/r['data_regions'])
 for a,n in [(0x5c4c8,74),(0x4e914,84),(0x4e9ec,26),(0x4e9e8,4),(0x77e98,80)]+[(a,n) for _,a,n in regions]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 for a in [0x5c4c8,0x4e914,0x4e9ec,0x4e9e8,0x77e98,0x4ea10]:
  rea=read(OUT/f'rea-{a:x}.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'))
  if a==0x77e98:assert rea['normalized_result']['body']['total_bytes']==80 and rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
  else:assert rea['error']['code']=='invalid_request' and 'No procedure exists' in str(rea)
 assert e['device_module_body_ranges']==[{'start':'0x5c4c8','bytes':74},{'start':'0x4e914','bytes':84}] and e['device_module_total_bytes']==158 and e['native_rtc_bytes']==26 and e['native_thunk_bytes']==4 and e['native_reset_adapter_bytes']==80 and e['supplemental_noop_bytes']==r['source_noop_compiled_bytes_equal']==2 and e['source_data_bytes']==r['source_data_bytes']==248
 assert e['rtc_callback_signature']=='void(uint32_t)' and e['rtc_callback_signature_header_sha256']==sha(ROOT/e['rtc_callback_signature_header'])
 assert e['leaf_provider_fixtures'] and not e['full_linked_graph_execution_verified'] and not e['physical_reset_w1c_semantics_verified'] and not e['locked_ownership_changed'] and e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['device_module_original_row']==next(row for row in rows if row['image']=='application' and row['entry']=='0x0005c4c8') and e['device_module_original_row']['size']=='158' and not any(row['image']=='application' and row['entry']=='0x0004ea10' for row in rows)
 from audit_source_frontier import section_bytes
 for name,a,n in regions:
  if name=='rtc_callback':continue # Relocatable source function pointer, bound in the verification ELF.
  data=section_bytes(obj,'.r1.device.startup.'+name,executable=name=='rtc_noop');assert len(data)==n and data==raw[a-0x27000:a-0x27000+n]
 assert section_bytes(obj,'.r1.device.startup.rtc_noop',executable=True)==bytes.fromhex('7047')
 relocs=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_ABS32)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.r1.device.startup.rtc_callback',str(obj)],text=True),re.M);assert relocs==[('00000000','R_ARM_ABS32','r1_native_rtc_startup_tick_noop')]
 initial=read(OUT/'initial-typed-return-verification.json');assert e['initial_typed_return_receipt_sha256']==sha(OUT/'initial-typed-return-verification.json') and initial['object_sha256']==r['object_sha256'] and initial['module_r0_excluded_from_typed_equivalence'] and e['raw_r0_checks_strengthened_without_firmware_object_change']
 bp=BASE/'native-device-reset-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-device-reset-runtime.o') and len(bundle['application_imports_resolved'])==11 and bundle['remaining_application_imports']==['ble_dfu_buttonless_async_svci_init','cm_backtrace_init'] and len(bundle['undefined_symbols'])==68 and not bundle['full_provider_execution_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for path,h in bundle['inputs'].items():assert sha(ROOT/path)==h,path
 for group in ['provider_reports','objects']:
  for path,h in bundle[group].items():assert sha(BASE/path)==h,path
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-device-reset-runtime.o')[0]==bundle['undefined_symbols'] and {'r1_device_preinitialize_3510c','r1_gxt310_self_check','r1_reset_reason_decode_and_report'}<=set(bundle['undefined_symbols'])
 print('Device/reset startup authenticated:16377 cases; eleven direct app imports source-linked; two direct/68 total imports and full ABI/MMIO/image gates remain open')
if __name__=='__main__':audit()
