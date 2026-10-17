#!/usr/bin/env python3
"""Bind LIS auxiliaries, attributed routing condition, native bytes and regression evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-lis-aux';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());route=json.loads((out/'route-verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-lis-call-frames';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-lis-call-frames-runtime.o')==b['parent_object_sha256'] and sha(out/'native-lis-aux-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-lis-aux-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==26 and sha(out/'aux-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'aux-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_lis2dw12_aux16_boundary','r1_lis2dw12_aux20_boundary'] and not b['newly_exposed_imports']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;receipt=json.loads(path.read_text());n=(receipt.get('structuredContent') or {}).get('normalized_result',{})
  if 'bytes_hex' in n:
   a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 assert b['upstream_pin']=='8d4bd522015004a9646102702901ba5a15ec6d39' and b['upstream_license']=='BSD-3-Clause' and not b['exact_vendor_checkout_proven'] and not b['unmodified_upstream_body']
 vendor=ROOT/('vendor-cache/r1/st-lis2dw12-'+b['upstream_pin']);raw=(vendor/'lis2dw12_reg.c').read_bytes();body=raw[b['source_slice_start']:b['source_slice_end']];assert hashlib.sha256(body).hexdigest()==b['original_slice_sha256'] and b['original_logic'] in body.decode();generated=(out/'st-route-byte.c').read_text();assert (vendor/'LICENSE').read_text() in generated and b['original_logic'].replace('\r\n','\n').replace('val->','u4.reg.').replace('ctrl5_int2_pad_ctrl.','u5.reg.').replace('reg.interrupts_enable','u7.reg.interrupts_enable') in generated and not undefined_symbols(out/'st-route-byte.o')[0]
 sections=allocated_sections(out/'native_lis_aux.o')
 for name,a,size in [('disable_ring',0x75248,36),('disable_sdk',0x75274,28),('enable_ring',0x75340,52),('enable_sdk',0x7537c,48)]:assert sections['.r1.lis.tap.'+name][2]==size and sections['.r1.lis.tap.'+name][4]==hashlib.sha256(binary[a-0x27000:a-0x27000+size]).hexdigest()
 assert r['comparisons']==4320 and r['counts']==dict(enable=2160,disable=2160) and r['observation_counts']==dict(read=4500,write=3960,custom_read=24840,delay=0,mode=11520,ring=2880,sdk=2160) and r['trace_sha256']=='a648bd55e58264d22fa1efd4dec91be5d2105257f2b7acd6ca24480ae366658c'
 assert route['comparisons']==73468 and route['counts']==dict(exhaustive_set=65536,matrix_set=4860,get=3072) and route['matching_faults']==108 and route['observation_counts']==dict(read=140624,write=131648) and route['trace_sha256']=='ebc15577e401c3fdf2f5ebfe6cdf966c7c6eeaa446517376ba00bab3ee637d8c'
 for proof,driver in [(r,'verify_native_lis_aux.py'),(route,'verify_native_lis_routes.py')]:
  assert sha(out/'report.json')==proof['report_sha256'] and sha(out/'native-lis-aux-runtime.o')==(proof.get('graph_sha256') or proof['object_sha256']) and sha(ROOT/('r1/tools/'+driver))==proof['driver_sha256'] and sha(app)==proof['application_sha256']
  for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not proof[flag]
 for flag in ['actual_two_auxiliaries_route_condition_register_helpers_default_transport_and_registry','only_bus_custom_read_delay_and_logging_callbacks_are_fixtures','tap_sequences_fresh_log_mode_ignored_status_and_raw_saved_r3_checked','raw_r0_callee_sp_context_and_outer_frame_checked']:assert r[flag]
 for flag in ['actual_route_get_set_pure_st_condition_and_read_write_proxies','only_transport_callbacks_are_fixtures','all_65536_ctrl4_ctrl5_pairs_against_independent_mask_oracle','scratch_status_saved_r2_r3_callee_sp_context_data_and_aliases_checked']:assert route[flag]
 old=out/'pre-null-fixture-guard';prior=json.loads((old/'route-verification.json').read_text());assert sha(old/'verify_native_lis_routes.py')==prior['driver_sha256'] and prior['matching_faults']==396 and prior['trace_sha256']=='bbbe5d4ef0addd068c3296e7fcd01a755c1a603d27348ecde9171216368bf8e4'
 print('LIS auxiliaries/routes:4320 composed +73468 direct comparisons;164 exact text bytes;26 main imports')
if __name__=='__main__':audit()
