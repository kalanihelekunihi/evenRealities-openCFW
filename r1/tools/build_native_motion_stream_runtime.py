#!/usr/bin/env python3
"""Compose motion adapters around the selected provider and existing NV/clock sources."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-motion-stream-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-stream-singletons-runtime','native-stream-singletons-runtime.o','linked_sha256'),('native-motion-stream','native_motion_stream.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-motion-stream-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True)
 u,d=undefined_symbols(linked);old=undefined_symbols(objects[0])[0];assert sorted(set(old)-set(u))==['r1_motion_initialize_entry','r1_motion_stream_close_boundary','r1_motion_thirty_sample_batch_producer','r1_native_motion_interrupt'] and sorted(set(u)-set(old))==['r1_motion_probe_and_select_provider'] and len(u)==20
 graph=out/'motion-stream-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[arg for root in ['r1_motion_initialize_entry','r1_motion_stream_close_boundary','r1_motion_thirty_sample_batch_producer','r1_native_motion_interrupt','r1_motion_selected_provider_initialize','r1_motion_selected_fifo_read','r1_motion_calibration_bypassed','r1_motion_calibration_read'] for arg in ['-u',root]],str(linked),'-o',str(graph)],check=True);gu=undefined_symbols(graph)[0];assert set(gu)<=set(u)
 r=dict(graph_object_sha256=sha(graph),graph_undefined_symbols=gu,inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=['r1_motion_initialize_entry','r1_motion_stream_close_boundary','r1_motion_thirty_sample_batch_producer','r1_native_motion_interrupt'],newly_exposed_imports=['r1_motion_probe_and_select_provider'],canonical_reset_context_reused=True,composed_runtime_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Motion adapters linked;provider probing remains explicit:20 imports')
if __name__=='__main__':main()
