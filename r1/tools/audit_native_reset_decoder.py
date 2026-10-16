#!/usr/bin/env python3
"""Bind reset decoder body/ranges/constants, scratch seed bridge and open providers."""
import csv,hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-reset-decoder';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 r=read(OUT/'verification.json');rp=OUT/'report.json';report=read(rp);e=read(OUT/'evidence.json');app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';raw=app.read_bytes();obj=OUT/'native_reset_decoder.o'
 assert r['callback_observations_per_side']==1965056 and r['diagnostic_provider_calls_per_side']==314992 and r['byte_provider_calls_per_side']==124400 and r['trace_sha256']=='0135fc67560a75de4496634fcdef2aad3c68e87aafa13004c7b96b062021b014'
 assert r['comparisons']==114240
 for flag in ['all_128_recognized_flag_combinations','unknown_bits_and_zero_reason_distinguished','recognized_mask_0x7000f_checked','full_width_getter_statuses_and_values','fresh_pc_lr_and_tag_value_reloads_after_callback_mutations','tag_retested_after_logging_before_conditional_caller_query','four_byte_diagnostic_initial_words_and_incoming_r3_seed_checked','raw_r0_stack_callee_integer_full_observed_nonstack_ram_and_typed_callback_order_args_checked','diagnostic_pointer_addresses_normalized_private_frame_gate','diagnostic_and_logging_bodies_are_named_fixtures','source_raw_seed_bridge_to_c_kernel','candidate_native_body_execution_forbidden','unicorn_memory_write_hooks_disabled']:assert r[flag],flag
 assert not r['whole_startup_graph_executed'] and not r['physical_reset_or_retention_verified'] and not r['instruction_identity'] and not r['full_raw_abi_verified'] and r['source_constant_data_bytes']==1396
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_reset_decoder.py') and r['report_sha256']==sha(rp) and r['object_sha256']==sha(obj)==report['units'][0]['object_sha256'] and r['layout_sha256']==sha(ROOT/r['layout']) and r['application_sha256']==sha(app) and r['data_regions_sha256']==sha(ROOT/r['data_regions'])
 for p,h in report['inputs'].items():assert sha(ROOT/p)==h,p
 assert report['units'][0]['source_sha256']==sha(ROOT/report['units'][0]['source']) and not report['application_linked'] and not report['instruction_identity']
 for group in ['ghidra','rea']:
  for p,h in e[group].items():assert sha(OUT/p)==h,p
 regions=read(ROOT/e['data_regions']);assert e['data_regions_sha256']==sha(ROOT/e['data_regions']) and sum(n for _,_,n in regions)==1396
 for a,n in [(0x8198c,620),(0x81fb8,134)]+[(a,n) for _,a,n in regions]:assert bytes(read(OUT/f'ghidra-{a:x}.json')['data'])==raw[a-0x27000:a-0x27000+n]
 rea=read(OUT/'rea-8198c.json');rea=rea.get('structuredContent') or json.loads(next(x['text'] for x in rea['content'] if x['type']=='text'));assert rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea['normalized_result']['body']['ranges']==[{'start':'0x8198c','end':'0x81bf7'},{'start':'0x81fb8','end':'0x8203d'}] and rea['normalized_result']['body']['total_bytes']==754
 assert e['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and e['frozen_corpus_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and e['native_body_bytes']==754 and not e['locked_ownership_changed'] and not e['whole_image_identity'] and not e['upstream_vendor_implementation_claim']
 rows=list(csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()));assert e['ownership_row']==next(x for x in rows if x['image']=='application' and x['entry']=='0x0008198c')
 from audit_source_frontier import section_bytes
 for name,a,n in regions:
  if name in ['lr_pointer','dif_pointer']:continue
  assert section_bytes(obj,'.r1.reset.decode.'+name,executable=False)==raw[a-0x27000:a-0x27000+n]
 for name,target in [('lr_pointer','lr_ring'),('dif_pointer','dif_ring')]:
  relocs=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_ABS32)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.r1.reset.decode.'+name,str(obj)],text=True),re.M);assert relocs==[('00000000','R_ARM_ABS32','r1_reset_decode_'+target)]
 relocs=re.findall(r'^([0-9a-f]{8})\s+(R_ARM_THM_JUMP24)\s+(\S+)',subprocess.check_output(['arm-none-eabi-objdump','-r','-j','.text.r1_reset_reason_decode_and_report',str(obj)],text=True),re.M);assert relocs==[('00000000','R_ARM_THM_JUMP24','r1_reset_reason_decode_kernel')]
 ctype=read(BASE/'native-ctype/evidence.json');assert ctype['window_address']=='0xbda90' and ctype['source_data_bytes']==257 and e['shared_dif_ctype_overlap_bytes']==0xbda90+257-0xbdb78==25 and e['overlap_bytes_not_unique_image_coverage']
 overlap=section_bytes(obj,'.r1.reset.decode.dif_ring',executable=False)[:25];assert overlap==raw[0xbdb78-0x27000:0xbdb91-0x27000]==bytes(read(BASE/'native-ctype/ghidra-bda90.json')['data'])[-25:]
 bp=BASE/'native-reset-decoder-runtime/report.json';bundle=read(bp);assert bundle['linked_sha256']==sha(bp.parent/'native-reset-decoder-runtime.o') and len(bundle['application_imports_resolved'])==13 and bundle['remaining_application_imports']==[] and len(bundle['undefined_symbols'])==65 and 'r1_reset_reason_decode_and_report' not in bundle['undefined_symbols'] and {'r1_reset_trace_byte_read','r1_reset_trace_program_counter_read','r1_reset_trace_return_address_read'}<=set(bundle['undefined_symbols']) and not bundle['whole_startup_graph_executed'] and not bundle['physical_reset_or_retention_verified'] and not bundle['application_linked'] and not bundle['original_instruction_identity']
 for p,h in bundle['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in bundle[group].items():assert sha(BASE/p)==h,p
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(bp.parent/'native-reset-decoder-runtime.o')[0]==bundle['undefined_symbols']
 print('Reset decoder authenticated:114240 cases;1396 constant bytes;three retained getters/65 startup imports and shared-data/private ABI/hardware/image gates remain')
if __name__=='__main__':audit()
