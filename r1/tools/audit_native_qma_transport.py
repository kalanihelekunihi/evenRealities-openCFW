#!/usr/bin/env python3
"""Authenticate native QMA transport/IRQ/FIFO contracts and distinct hardened evidence."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 out=BASE/'native-qma-transport';b=json.loads((out/'report.json').read_text());r=json.loads((out/'verification.json').read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';binary=app.read_bytes()
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for p,h in b['comparison_only_inputs'].items():assert sha(ROOT/p)==h,p
 for row in b['units']:assert row['compiled'] and sha(ROOT/row['source'])==row['source_sha256'] and sha(Path(row['command'][-1]))==row['object_sha256']
 parent=BASE/'native-bma-initialize';assert sha(parent/'report.json')==b['parent_report_sha256'] and sha(parent/'native-bma-initialize-runtime.o')==b['parent_object_sha256'] and sha(out/'native-qma-transport-runtime.o')==b['linked_sha256']==r['object_sha256'] and undefined_symbols(out/'native-qma-transport-runtime.o')[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==20 and sha(out/'qma-source.o')==b['graph_object_sha256'] and undefined_symbols(out/'qma-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_qma6100_bounded_fifo_read','r1_qma6100_chip_id','r1_qma6100_irq_boundary'] and not b['newly_exposed_imports'] and b['owner_authorized_native_reconstruction'] and not b['unlicensed_qst_source_is_build_input'] and not b['existing_hardened_reconstruction_substituted'] and b['runtime_prefix_bytes']==12 and not b['full_sensor_state_extent_proven']
 assert r['comparisons']==17074 and r['counts']==dict(read=3026,write=4032,delay=4,chip=1344,irq=1024,fifo=6382,normalized=1262) and r['matching_faults']==2 and r['observation_counts']==dict(read=39282,write=10190,cycles=271566,mode=15270,ring=1440,sdk=1440,any_motion=392,double_tap=371,acquire=842,release=841) and r['trace_sha256']=='09039ade6a0173324a0165df6bebcc5ca654c281ce9fec6e5c15351451bf14f9'
 assert sha(out/'report.json')==r['report_sha256'] and sha(ROOT/'r1/tools/verify_native_qma_transport.py')==r['driver_sha256']
 for p,h in r['evidence'].items():
  path=out/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result']
  if 'bytes_hex' in n:
   a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 sections=allocated_sections(out/'native_qma_transport.o');cold=BASE/'native-scatter-data/observed-initialized-data.bin';assert sha(cold)=='87fdee392022fdbe23dd0daf3e859fb14f3ce26ba3e8403aab56dc9d9a913317';runtime=cold.read_bytes()[0x20007698-0x200064a8:0x200076a4-0x200064a8];assert runtime==bytes.fromhex('120000000000000000000000') and sections['.r1.qma.runtime'][2:]==[12,4,hashlib.sha256(runtime).hexdigest()]
 spans=out/'fifo-text-spans.json';assert sha(spans)==b['fifo_text_spans_sha256'];rows=json.loads(spans.read_text());assert len(rows)==4 and sum(x['size'] for x in rows)==144
 for row in rows:
  a=int(row['address'],16);data=binary[a-0x27000:a-0x27000+row['size']];assert data.split(b'\0')[0].decode()==row['text'] and sections[row['section']][2]==row['size'] and sections[row['section']][4]==hashlib.sha256(data).hexdigest()
 assert int.from_bytes(binary[0x86e64-0x27000:0x86e68-0x27000],'little')==0x9a6a0 and binary[0x9a6a0-0x27000:0x9a6a6-0x27000].hex()=='0338fdd87047'
 for flag in ['actual_six_qma_bodies_normalizer_motion_requests_and_registry','only_bus_cycle_log_and_event_callbacks_are_fixtures','retry_bound_last_failure_delay_fresh_address_and_irq_rebinding_checked','zero_length_fifo_payload_reset_ignored_errors_and_unwritten_id_checked','raw_r0_saved_r2_r3_callee_sp_runtime_data_and_request_pointers_checked']:assert r[flag]
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 assert '0x9a6a0' in (out/'pre-cycle-fixture-address-fix/r1-qma-transport-verification.log').read_text()
 print('QMA transport/ID/IRQ/FIFO:17074 comparisons;12 cold runtime+144 text bytes;20 main imports')
if __name__=='__main__':audit()
