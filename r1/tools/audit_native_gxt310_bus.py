#!/usr/bin/env python3
"""Bind native bus record behavior, attributable cold source state and runtime."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-gxt310-bus';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_gxt310_bus.o'
 assert r['comparisons']==69340 and r['counts']=={'cache':60,'acquire':60,'release':60,'read':17280,'write':17280,'read_thunk':17280,'write_thunk':17280,'persistent_sequence':40} and r['callback_observations_per_side']==69644 and r['trace_sha256']=='dff0ccf034c41661c3074375a322e9aad9be62765ba58d16f45f4c46da418d05'
 for flag in ['all_seven_source_entries_executed','request_field_widths_and_store_order_checked','read_pointer_unconditionally_replaced','null_write_pointer_preserves_prior_record_pointer','zero_dispatch_status_returns_one','cache_retries_and_cached_handle_reuse','callback_mutated_handle_and_padding','persistent_multi_call_record_sequences','raw_r0_callee_integer_stack_full_observed_nonstack_ram_and_callback_args_checked','executed_store_observer_with_full_ram_reconciliation','registry_dispatch_and_lookup_are_named_fixtures','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['whole_startup_graph_executed'] and not r['physical_bus_verified'] and not r['instruction_identity'] and not r['full_raw_abi_verified'] and r['source_state_bytes']==24 and r['source_name_bytes']==8
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_gxt310_bus.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app) and r['analysis_elf_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 assert report['units'][0]['source_sha256']==sha(ROOT/report['units'][0]['source']) and not report['application_linked'] and not report['instruction_identity']
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 regions=[(0x50efc,8),(0x50f04,4),(0x50f08,20),(0x50f1c,4),(0x50f20,8),(0x50f28,8),(0x50f30,4),(0x50f34,36),(0x50f58,4),(0x50f5c,38),(0x50f84,4),(0x6f640,4),(0x6f644,4)]
 for a,n in regions:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 entries=[(0x50efc,8),(0x50f08,20),(0x50f28,8),(0x50f34,36),(0x50f5c,38),(0x6f640,4),(0x6f644,4)]
 for a,n in entries:
  rea=read(OUT/f'rea-{a:x}.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea['normalized_result']['body']['ranges']==[{'start':hex(a),'end':hex(a+n-1)}] and rea['normalized_result']['body']['total_bytes']==n
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['native_unique_code_bytes']==118 and e['native_pointer_literal_bytes']==20 and not e['locked_ownership_changed'] and not e['whole_image_identity'] and not e['upstream_vendor_implementation_claim'] and not e['whole_initialized_data_source_owned']
 history=read(OUT/e['initial_inlined_candidate_manifest']);assert e['initial_inlined_candidate_manifest_sha256']==sha(OUT/e['initial_inlined_candidate_manifest']) and history['status']=='superseded-before-admission' and e['native_tail_structure_retained_with_core_noinline']
 for old in history['files'].values():assert sha(OUT/'initial-inlined-candidate'/old['snapshot'])==old['sha256']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_rows']==[x for x in rows if x['image']=='application' and int(x['entry'],16) in dict(entries)]
 from audit_source_frontier import section_bytes
 cold=ROOT/e['cold_observation'];cr=ROOT/e['cold_receipt'];assert e['cold_observation_sha256']==sha(cold)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and e['cold_receipt_sha256']==sha(cr) and read(cr)['observed_initialized_data_sha256']==sha(cold) and read(cr)['application_sha256']==sha(app)
 initial=section_bytes(obj,'.r1.gxt.bus.state',executable=False);assert len(initial)==24 and initial==cold.read_bytes()[0x1250:0x1268] and initial.hex()==e['cold_source_bytes_hex']=='000000001200000000000000010000000000000001000000'
 assert section_bytes(obj,'.r1.gxt.bus.name',executable=False)==raw[0x50f20-0x27000:0x50f28-0x27000]
 for name,target in [('r1_gxt310_register_read_native','r1_gxt310_transfer_read_native'),('r1_gxt310_register_write_native','r1_gxt310_transfer_write_native')]:
  relocs=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_THM_JUMP24)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.text.'+name,str(obj)],text=True),re.M);assert relocs==[('00000000','R_ARM_THM_JUMP24',target)]
 bp=BASE/'native-gxt310-bus-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-gxt310-bus-runtime.o') and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==65 and not bundle['whole_startup_graph_executed'] and not bundle['physical_i2c_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-gxt310-bus-runtime.o')[0]==bundle['undefined_symbols'] and not {'r1_i2c2_handle_cache','r1_gxt310_bus_acquire','r1_gxt310_bus_release','r1_gxt310_register_read_native','r1_gxt310_register_write_native'}&set(bundle['undefined_symbols'])
 print('GXT bus authenticated:69340 cases;24-byte cold source state and source registry linkage;65 startup imports and mode/hardware/ABI/image gates remain')
if __name__=='__main__':audit()
