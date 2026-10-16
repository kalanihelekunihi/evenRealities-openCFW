#!/usr/bin/env python3
"""Bind native LIS register comparisons to attributed pinned source and byte receipts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_lis_registers import FUNCTIONS
 out=BASE/'native-lis-registers';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text())
 assert r['comparisons']==55767 and len(r['counts'])==18 and r['counts']['lis2dw12_write_reg']==75 and all(r['counts']['lis2dw12_'+x]==3276 for x in FUNCTIONS.values()) and r['observation_counts']==dict(read=55692,write=42123) and r['trace_sha256']=='8eaf8ead8309d76e4348105b2b5587c298a34f63d43ca84b8ea3e122e6313763'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'registers-source.o')==r['graph_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_lis_registers.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result']
  if 'bytes_hex' in n:
   a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 assert b['upstream_pin']=='8d4bd522015004a9646102702901ba5a15ec6d39' and b['upstream_license']=='BSD-3-Clause' and not b['exact_vendor_checkout_proven'] and not b['unmodified_upstream_body']
 vendor=ROOT/('vendor-cache/r1/st-lis2dw12-'+b['upstream_pin']);raw=(vendor/'lis2dw12_reg.c').read_bytes();generated=(out/'st-register-frames.c').read_text();assert (vendor/'LICENSE').read_text() in generated
 assert len(b['source_slices'])==17
 for row in b['source_slices']:
  assert hashlib.sha256(raw[row['start']:row['end']]).hexdigest()==row['original_slice_sha256'] and len(row['adaptations'])==3 and row['name']+'_body' in generated
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-lis-identity';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-lis-identity-runtime.o')==b['parent_object_sha256'] and sha(out/'native-lis-registers-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-lis-registers-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==29 and not undefined_symbols(out/'registers-source.o')[0]
 for flag in ['actual_17_attributed_bodies_native_write_proxy_and_read_proxy','only_transport_callbacks_are_fixtures','scratch_pointer_status_saved_r3_callee_sp_context_and_data_ram_checked','all_byte_values_and_old_register_values_tested']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','exact_vendor_checkout_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for directory,address,native,source in [('pre-bdu-attribution-fix','0x750b8',85,81),('pre-tap-axis-attribution-fix','0x7581a',42,138)]:
  h=out/directory;c=json.loads((h/'counterexample.json').read_text());assert c['address']==address and c['native_written_byte']==native and c['rejected_source_written_byte']==source
  prior=json.loads((h/'report.json').read_text());assert sha(h/'registers-source.o')==prior['graph_object_sha256'] and sha(h/'native-lis-registers-runtime.o')==prior['linked_sha256'] and 'AssertionError' in (h/'r1-lis-registers-verification.log').read_text()
  for row in prior['units']:assert sha(h/Path(row['source']).name)==row['source_sha256'] and sha(h/Path(row['command'][-1]).name)==row['object_sha256']
 print('LIS register bodies:55767 comparisons;17 ST slices and corrected attribution counterexamples authenticated')
if __name__=='__main__':audit()
