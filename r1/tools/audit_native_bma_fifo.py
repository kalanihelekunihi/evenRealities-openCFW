#!/usr/bin/env python3
"""Bind Bosch FIFO source, attributed mask, exact strings and composed execution."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-bma-fifo';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-bma-feature-io';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-bma-feature-io-runtime.o')==b['parent_object_sha256'] and sha(out/'native-bma-fifo-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-bma-fifo-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==24 and sha(out/'fifo-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'fifo-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_bma456w_fifo_read'] and not b['newly_exposed_imports']
 assert r['comparisons']==76397 and r['counts']==dict(length=65984,bytes=3599,fifo=3599,normalized=3215) and r['matching_faults']==6 and r['observation_counts']==dict(read=84872,write=6406,delay=4966,cycles=3902,mode=11682,ring=2784,sdk=2784,acquire=3215,release=3213) and r['trace_sha256']=='d8c352c4e5f9d2fbd6a39d9214a86b2689ecc4497c2265fc4b9c6bd96b99d4a5'
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_bma_fifo.py')==r['driver_sha256']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 assert b['upstream_pin']=='3266db2c5de15be1a00232b8c0f2fd23e07934e0' and b['upstream_license']=='BSD-3-Clause' and len(b['adaptations'])==2
 vendor=ROOT/'third-party/upstream/bosch-bma456';raw=(vendor/'bma4.c').read_bytes();body=raw[b['source_slice_start']:b['source_slice_end']];generated=(out/'bosch-fifo-mask.c').read_text();assert hashlib.sha256(body).hexdigest()==b['original_slice_sha256'] and b['original_assignment'] in body.decode() and b['original_assignment'] in generated and (vendor/'LICENSE').read_text() in generated and not undefined_symbols(out/'bosch-fifo-mask.o')[0]
 sections=allocated_sections(out/'native_bma_fifo.o')
 for name,a,size in [('disable_ring',0x542b4,52),('disable_sdk',0x542e8,48),('read_ring',0x54318,40),('read_sdk',0x54340,36),('enable_ring',0x54364,52),('enable_sdk',0x54398,44)]:assert sections['.r1.bma.fifo.'+name][2]==size and sections['.r1.bma.fifo.'+name][4]==hashlib.sha256(binary[a-0x27000:a-0x27000+size]).hexdigest()
 for flag in ['actual_three_fifo_bodies_normalizer_full_read_write_power_graph_and_registry','only_transport_delay_cycle_and_logging_callbacks_are_fixtures','all_65536_wire_lengths_against_independent_14bit_oracle','zero_guard_byte_length_wrap_signed_count_alias_and_failure_asymmetry_checked','native_callback_scratch_pointer_callee_sp_context_ram_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 print('Bosch FIFO:76397 comparisons,6 faults;all wire lengths;272 exact text bytes;main24 imports')
if __name__=='__main__':audit()
