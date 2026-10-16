#!/usr/bin/env python3
"""Compose motion selector and native provider wrappers with explicit leaf gates."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-motion-selection-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-motion-stream-runtime','native-motion-stream-runtime.o','linked_sha256'),('native-motion-selection','native_motion_selection.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-motion-selection-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True)
 u,d=undefined_symbols(linked);old=undefined_symbols(objects[0])[0];assert sorted(set(old)-set(u))==['r1_motion_probe_and_select_provider'] and sorted(set(u)-set(old))==['r1_bma456w_configure_boundary', 'r1_bma456w_fifo_normalized', 'r1_bma456w_identity_probe', 'r1_lis2dw12_aux16_boundary', 'r1_lis2dw12_aux20_boundary', 'r1_lis2dw12_configure_boundary', 'r1_lis2dw12_fifo_normalized', 'r1_lis2dw12_identity_probe', 'r1_qma6100_chip_id', 'r1_qma6100_configure_boundary', 'r1_qma6100_fifo_normalized', 'r1_qma6100_irq_boundary'] and len(u)==31
 graph=out/'motion-selection-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[arg for root in ['r1_motion_probe_and_select_provider', 'r1_motion_refresh_selection', 'r1_motion_bus_acquire', 'r1_motion_bus_release', 'r1_lis2dw12_probe_wrapper', 'r1_bma456w_probe_wrapper', 'r1_qma6100_probe_wrapper', 'r1_lis2dw12_configuration_wrapper', 'r1_bma456w_configuration_wrapper', 'r1_qma6100_configuration_wrapper', 'r1_lis2dw12_interrupt_noop', 'r1_bma456w_interrupt_noop', 'r1_qma6100_interrupt_wrapper', 'r1_motion_selected_provider_initialize', 'r1_native_motion_interrupt', 'r1_motion_selected_fifo_read'] for arg in ['-u',root]],str(linked),'-o',str(graph)],check=True);gu=undefined_symbols(graph)[0];assert set(gu)<=set(u)
 r=dict(graph_object_sha256=sha(graph),graph_undefined_symbols=gu,inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=['r1_motion_probe_and_select_provider'],newly_exposed_imports=['r1_bma456w_configure_boundary', 'r1_bma456w_fifo_normalized', 'r1_bma456w_identity_probe', 'r1_lis2dw12_aux16_boundary', 'r1_lis2dw12_aux20_boundary', 'r1_lis2dw12_configure_boundary', 'r1_lis2dw12_fifo_normalized', 'r1_lis2dw12_identity_probe', 'r1_qma6100_chip_id', 'r1_qma6100_configure_boundary', 'r1_qma6100_fifo_normalized', 'r1_qma6100_irq_boundary'],canonical_reset_context_reused=True,composed_runtime_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Motion selection linked;12 concrete provider imports exposed:31 imports')
if __name__=='__main__':main()
