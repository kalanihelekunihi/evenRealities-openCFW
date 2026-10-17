#!/usr/bin/env python3
"""Authenticate complete Bosch feature/power transport graph and native error contracts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 out=BASE/'native-bma-feature-io';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-bma-reads';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-bma-reads-runtime.o')==b['parent_object_sha256'] and sha(out/'native-bma-feature-io-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-bma-feature-io-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==25 and sha(out/'feature-io-source.o')==b['graph_object_sha256'] and not undefined_symbols(out/'feature-io-source.o')[0]
 assert b['closed_parent_imports']==['r1_bma4_feature_chunk_read_boundary','r1_bma4_set_advance_power_save_boundary'] and not b['newly_exposed_imports']
 assert r['comparisons']==11902 and r['counts']==dict(write_direct=3488,write=4384,power=752,reset=32,increment=392,chunk_read=928,chunk_write=934,read=992) and r['matching_faults']==140 and r['continued_after_error_cases']==160 and r['observation_counts']==dict(read=14074,write=23637,delay=17953) and r['trace_sha256']=='bb1f5ab62c129e8d0d0114ceed1bc4f437846dd494fb2dd59ea71a1d6f9fbc07'
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_bma_feature_io.py')==r['driver_sha256']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 assert b['upstream_pin']=='3266db2c5de15be1a00232b8c0f2fd23e07934e0' and b['upstream_license']=='BSD-3-Clause' and len(b['source_slices'])==2
 vendor=ROOT/'third-party/upstream/bosch-bma456';raw=(vendor/'bma4.c').read_bytes();generated=(out/'bosch-feature-updates.c').read_text();assert (vendor/'LICENSE').read_text() in generated
 for row in b['source_slices']:assert hashlib.sha256(raw[row['start']:row['end']]).hexdigest()==row['original_slice_sha256'] and raw[row['start']:row['end']].decode()==row['body']
 assert b['power_assignment'] in b['source_slices'][0]['body'] and b['power_assignment'] in generated and len(b['address_assignments'])==4
 for line in b['address_assignments']:assert line in b['source_slices'][1]['body'] and line in generated
 assert not undefined_symbols(out/'bosch-feature-updates.o')[0]
 for flag in ['actual_seven_bodies_read_write_graph_helpers_nullcheck_requests_and_registry','public_feature_reads_with_actual_power_and_chunk_helpers','only_bus_raw_transport_and_delay_callbacks_are_fixtures','feature_error_continuation_wrap_index_and_fresh_delay_fields_checked','address_updates_against_independent_oracle','native_callback_scratch_pointer_callee_sp_context_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 old=out/'pre-public-read-regression';prior=json.loads((old/'verification.json').read_text());assert sha(old/'verify_native_bma_feature_io.py')==prior['driver_sha256'] and prior['comparisons']==10910 and prior['trace_sha256']=='bc94c4d38541802a3c93ab04aa9642d3dabeced7e86d427952105b5cd401d0ab' and prior['object_sha256']==r['object_sha256']
 assert 'AssertionError' in (out/'pre-oracle-guard/r1-bma-feature-io-verification.log').read_text()
 print('Bosch feature IO:11902 comparisons,140 faults,160 error-continuation cases;selected graph zero imports;main25')
if __name__=='__main__':audit()
