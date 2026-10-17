#!/usr/bin/env python3
"""Authenticate native Bosch interface bindings, attributed helper and bounded execution."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-bma-interface';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-lis-aux';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-lis-aux-runtime.o')==b['parent_object_sha256'] and sha(out/'native-bma-interface-runtime.o')==b['linked_sha256'] and undefined_symbols(out/'native-bma-interface-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==26 and sha(out/'interface-source.o')==b['graph_object_sha256']==r['object_sha256'] and not undefined_symbols(out/'interface-source.o')[0]
 assert r['comparisons']==4437 and r['counts']==dict(init=12,read=2160,write=2160,delay=9,check=96) and r['matching_faults']==1080 and r['observation_counts']==dict(read=540,write=540,cycles=8) and r['trace_sha256']=='130d5206b638cad71a52ee513cde69dcc59fbf1de0f7875af584894768190e2f'
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_bma_interface.py')==r['driver_sha256']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result']
  if 'bytes_hex' in n:
   a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 assert b['upstream_pin']=='3266db2c5de15be1a00232b8c0f2fd23e07934e0' and b['upstream_license']=='BSD-3-Clause' and b['upstream_function']=='null_pointer_check' and b['pinned_context_type_bytes']==52 and not b['full_native_context_extent_proven']
 vendor=ROOT/'third-party/upstream/bosch-bma456';raw=(vendor/'bma4.c').read_bytes();body=raw[b['source_slice_start']:b['source_slice_end']];assert hashlib.sha256(body).hexdigest()==b['original_slice_sha256'];generated=(out/'bosch-null-check.c').read_text();assert (vendor/'LICENSE').read_text() in generated and body.decode().replace('\r\n','\n').replace('static int8_t null_pointer_check','int8_t r1_bma4_null_pointer_check',1) in generated
 sections=allocated_sections(out/'native_bma_interface.o');assert sections['.bss.r1.bma.context']==[8,3,52,4,hashlib.sha256(b'').hexdigest()] and sections['.r1.bma.bus_address'][2:]==[4,4,hashlib.sha256(bytes.fromhex('18000000')).hexdigest()]
 cold=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(cold)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317' and cold.read_bytes()[0x200076c0-0x200064a8:0x200076c4-0x200064a8]==bytes.fromhex('18000000') and 0x20007e04<=0x2001e4e8<0x2001e51c<=0x20007e04+0x340b4
 for flag in ['actual_four_native_entries_attributed_null_check_requests_and_registry','only_bus_and_cycle_callbacks_are_fixtures','raw_status_callee_sp_context_bytes_and_request_coordinates_checked','relocated_callback_function_identity_only_normalized']:assert r[flag]
 assert r['source_context_candidate_bytes']==52 and r['source_initialized_address_bytes']==4
 for flag in ['full_native_context_extent_proven','full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('BMA interface:4437 comparisons including1080 native faults; pinned layout and attributed null helper authenticated')
if __name__=='__main__':audit()
