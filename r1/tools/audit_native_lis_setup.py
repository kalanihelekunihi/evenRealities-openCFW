#!/usr/bin/env python3
"""Authenticate LIS multi-register setup source, attribution and native evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-lis-setup';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==26000 and len(r['counts'])==4 and set(r['counts'].values())=={6500} and r['observation_counts']==dict(read=37724,write=29516) and r['trace_sha256']=='d53fcefa6458c4852fe50e6ddf2433511f10c0749ea7f8564ab1fbbb62d850ec'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'setup-source.o')==r['graph_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_lis_setup.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 assert b['upstream_pin']=='8d4bd522015004a9646102702901ba5a15ec6d39' and b['upstream_license']=='BSD-3-Clause' and not b['exact_vendor_checkout_proven'] and not b['native_power_enum_matches_modern_st'] and b['native_second_read_error_still_writes_and_adds_status'] and not b['reg17_semantic_name_proven']
 vendor=ROOT/('vendor-cache/r1/st-lis2dw12-'+b['upstream_pin']);raw=(vendor/'lis2dw12_reg.c').read_bytes();generated=(out/'st-setup-frames.c').read_text();assert (vendor/'LICENSE').read_text() in generated
 assert len(b['source_slices'])==2
 for row in b['source_slices']:assert hashlib.sha256(raw[row['start']:row['end']]).hexdigest()==row['original_slice_sha256'] and len(row['adaptations'])==3 and row['name']+'_body' in generated
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-lis-registers';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-lis-registers-runtime.o')==b['parent_object_sha256'] and sha(out/'native-lis-setup-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-lis-setup-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==29 and not undefined_symbols(out/'setup-source.o')[0]
 for flag in ['actual_two_attributed_bodies_two_native_bodies_and_read_write_proxies','only_transport_callbacks_are_fixtures','scratch_pointer_status_saved_r2_r3_callee_sp_context_and_data_ram_checked','all_byte_values_and_old_register_values_tested','native_power_second_read_error_behavior_preserved']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','exact_vendor_checkout_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('LIS setup:26000 comparisons; attributed ODR/filter and distinct native power/error contracts authenticated')
if __name__=='__main__':audit()
