#!/usr/bin/env python3
"""Bind source reset/port graph to previously authenticated provider bodies."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-protocol-reset-port-runtime';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def audit():
 rp=OUT/'report.json';b=read(rp);r=read(OUT/'verification.json')
 assert r['events_per_side']==162816 and r['trace_sha256']=='a1ef84ddbb5420d45431f88ab8e968b288b0852756c1843f4e17f64fd1196651'
 assert r['comparisons']==36864 and r['counts']=={'reset':12288,'arm':12288,'tick':12288}
 for flag in ['actual_source_clear','actual_source_port_init_and_registration','only_scheduler_event_and_logging_bodies_are_fixtures','fragment_and_ingress_address_bindings_not_executed','one_byte_event_payload_checked_private_pointer_not_compared','source_callback_placed_at_native_address_for_pointer_equality','callback_native_body_execution_replaced_with_compiled_source','raw_r0_callee_sp_and_observed_nonstack_ram_checked']:assert r[flag]
 assert not r['whole_protocol_graph'] and not r['instruction_identity'] and not r['whole_image_complete'] and r['source_callback_bytes']==64
 assert r['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_reset_port_graph.py') and r['runtime_report_sha256']==sha(rp) and r['object_sha256']==b['graph_object_sha256']==sha(OUT/'protocol-reset-port-source.o') and r['layout_sha256']==sha(ROOT/'r1/source-config/runtime/native_protocol_reset_port_verification.ld') and r['application_sha256']==sha(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin')
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 for p,h in b['selected_objects'].items():assert sha(OUT/p)==h,p
 assert b['linked_sha256']==sha(OUT/'native-protocol-reset-port-runtime.o') and len(b['undefined_symbols'])==56 and b['callback_source_linked'] and not b['callback_graph_executed'] and not b['whole_startup_graph_executed'] and not b['instruction_identity'] and not b['whole_image_complete']
 from build_source_candidates import undefined_symbols
 assert undefined_symbols(OUT/'protocol-reset-port-source.o')[0]==b['graph_undefined_symbols'];u,d=undefined_symbols(OUT/'native-protocol-reset-port-runtime.o');assert u==b['undefined_symbols'] and {'r1_proto_port_init','r1_protocol_send_callback_set','r1_eus_ingress_plan_decode','r1_fragment_message','r1_stock_crc32_update'}<=set(d)
 old=read(BASE/'native-protocol-reset-runtime/report.json');assert set(old['undefined_symbols'])-set(u)=={'r1_proto_port_init'} and set(u)-set(old['undefined_symbols'])=={'r1_ble_event_dispatch','r1_eus_system_dispatch_plan_build','r1_health_registration_dispatcher'}
 from audit_source_frontier import section_bytes
 cu,cd=undefined_symbols(OUT/'crc32-source.o');assert cu==[] and 'r1_stock_crc32_update' in cd and 'r1_stock_crc16_modbus' not in cd
 assert section_bytes(OUT/'send-hook-cell.o','.r1.protocol.send_hook',executable=False)==bytes(4)
 print('Reset/port source graph authenticated:36864 cases;actual callback bodies source-linked with3 exposed dispatch seams;56 imports;frontier rows unchanged')
if __name__=='__main__':audit()
