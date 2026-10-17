#!/usr/bin/env python3
"""Authenticate Bosch identity/read graph and explicit unresolved feature contracts."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-bma-reads';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-bma-interface';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-bma-interface-runtime.o')==b['parent_object_sha256'] and sha(out/'native-bma-reads-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-bma-reads-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==27 and sha(out/'reads-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'reads-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_bma456w_identity_probe'] and b['newly_exposed_imports']==['r1_bma4_feature_chunk_read_boundary','r1_bma4_set_advance_power_save_boundary']
 assert r['comparisons']==7092 and r['counts']==dict(direct=4348,dispatch=1360,power=88,identity=1296) and r['matching_faults']==150 and r['observation_counts']==dict(raw=5223,bus=108,aps=130,chunk=36,mode=3072,ring=768,sdk=576) and r['trace_sha256']=='c9b0fb61e9cf40d338156dc2371807277f1238b2c6c51b3af84639bb8e799c96'
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_bma_reads.py')==r['driver_sha256']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 assert b['upstream_pin']=='3266db2c5de15be1a00232b8c0f2fd23e07934e0' and b['upstream_license']=='BSD-3-Clause' and len(b['adaptations'])==3
 vendor=ROOT/'third-party/upstream/bosch-bma456';raw=(vendor/'bma4.c').read_bytes();body=raw[b['source_slice_start']:b['source_slice_end']];assert hashlib.sha256(body).hexdigest()==b['original_slice_sha256'] and b['original_loop'] in body.decode();generated=(out/'bosch-read-copy.c').read_text();assert (vendor/'LICENSE').read_text() in generated and b['original_loop'].replace('\r\n','\n') in generated and 'const volatile struct bma4_dev *dev' in generated and 'uint16_t indx' in generated and not undefined_symbols(out/'bosch-read-copy.o')[0]
 sections=allocated_sections(out/'native_bma_reads.o')
 for name,a,size in [('init_ring',0x53bd8,40),('init_sdk',0x53c00,36),('id_ring',0x53c24,40),('id_sdk',0x53c4c,32)]:assert sections['.r1.bma.id.'+name][2]==size and sections['.r1.bma.id.'+name][4]==hashlib.sha256(binary[a-0x27000:a-0x27000+size]).hexdigest()
 for flag in ['actual_identity_dispatch_direct_copy_nullcheck_interface_requests_registry_and_power_get','only_transport_log_and_two_unresolved_feature_leaves_are_fixtures','raw_callback_status_full_word_check_and_low_byte_store_preserved','feature_register_full_word_comparison_and_error_gates_checked','native_callback_scratch_pointer_callee_sp_context_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('Bosch reads/identity:7092 comparisons,150 faults;148 exact text bytes;two feature helper imports remain')
if __name__=='__main__':audit()
