#!/usr/bin/env python3
"""Authenticate native selection, provider tables and explicit leaf dependencies."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def audit():
 from build_source_candidates import undefined_symbols
 from build_native_dfu_backend_runtime import allocated_sections
 from audit_source_frontier import section_bytes
 out=BASE/'native-motion-selection-runtime';r=json.loads((out/'verification.json').read_text());b=json.loads((out/'report.json').read_text())
 assert r['comparisons']==27650 and r['counts']==dict(select=8640,refresh=8640,acquire=90,release=90,lis_probe=90,bma_probe=90,qma_probe=90,lis_config=90,bma_config=90,qma_config=90,lis_irq=10,bma_irq=10,qma_irq=90,initialize=8640,interrupt=450,fifo=450) and r['observation_counts']==dict(acquire=8538,release=8538,lis_probe=15642,bma_probe=12186,qma_probe=9594,lis_config=2202,bma_config=2106,qma_config=1962,qma_irq=180,lis_fifo=90,bma_fifo=90,qma_fifo=90) and r['trace_sha256']=='3e755ba52288ed2c552f2221070a9805b6809988b200b79204f7811da5b44513'
 assert sha(out/'report.json')==r['report_sha256'] and sha(out/'motion-selection-source.o')==r['object_sha256']==b['graph_object_sha256'] and sha(ROOT/'r1/tools/verify_native_motion_selection.py')==r['driver_sha256']
 app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==r['application_sha256'];binary=app.read_bytes()
 for p,h in r['evidence'].items():
  path=BASE/'native-motion-selection'/p;assert sha(path)==h,p;n=json.loads(path.read_text())['structuredContent']['normalized_result'];a=int(n['address'],16);assert n['complete'] and bytes.fromhex(n['bytes_hex'])==binary[a-0x27000:a-0x27000+n['returned_bytes']]
 obj=BASE/'native-motion-selection/native_motion_selection.o';sections=allocated_sections(obj)
 for name,a in [('lis',0x9a730),('bma',0x9a748),('qma',0x9a718)]:assert r['provider_table_sha256'][name+'_table']==hashlib.sha256(binary[a-0x27000:a-0x27000+24]).hexdigest() and sections['.r1.motion.'+name+'.table'][:4]==[1,2,24,4]
 for name,a in [('lis2dw12',0x6f3b2),('bma456w',0x6f1da)]:assert section_bytes(obj,'.text.r1_'+name+'_interrupt_noop')==binary[a-0x27000:a-0x27000+2]
 for flag in ['actual_thirteen_bodies_registry_dispatch_and_selected_dispatch','only_bus_operations_sensor_leaf_providers_are_fixtures','ordered_full_width_ids_fresh_bus_selected_mutations_checked','raw_r0_callee_sp_selected_bus_and_ram_checked']:assert r[flag]
 assert r['source_owned_table_bytes']==72
 for flag in ['full_private_frame_history_verified','full_raw_abi_verified','real_provider_sensor_bus_execution_proven','instruction_identity','whole_image_complete','hardware_write_executed']:assert not r[flag]
 for p,h in b['inputs'].items():assert sha(ROOT/p)==h,p
 for group in ['provider_reports','objects']:
  for p,h in b[group].items():assert sha(BASE/p)==h,p
 linked=out/'native-motion-selection-runtime.o';assert sha(linked)==b['linked_sha256'] and undefined_symbols(linked)[0]==b['undefined_symbols'] and len(b['undefined_symbols'])==31 and undefined_symbols(out/'motion-selection-source.o')[0]==b['graph_undefined_symbols']
 assert b['closed_parent_imports']==['r1_motion_probe_and_select_provider'] and b['newly_exposed_imports']==['r1_bma456w_configure_boundary','r1_bma456w_fifo_normalized','r1_bma456w_identity_probe','r1_lis2dw12_aux16_boundary','r1_lis2dw12_aux20_boundary','r1_lis2dw12_configure_boundary','r1_lis2dw12_fifo_normalized','r1_lis2dw12_identity_probe','r1_qma6100_chip_id','r1_qma6100_configure_boundary','r1_qma6100_fifo_normalized','r1_qma6100_irq_boundary']
 for flag in ['composed_runtime_execution_verified','instruction_identity','whole_image_complete','hardware_write_executed']:assert not b[flag]
 print('Motion selection:27650 cases;72 source-owned table bytes;12 provider leaves remain explicit')
if __name__=='__main__':audit()
