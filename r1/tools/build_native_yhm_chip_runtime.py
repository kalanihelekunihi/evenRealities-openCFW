#!/usr/bin/env python3
"""Integrate native chip ID with existing source YHM read/write/discovery/state providers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-yhm-chip-runtime';out.mkdir(exist_ok=True);reports={};objects=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-device-checks','native_device_checks.o'),('native-dfu-vector-runtime','native-vector-startup-runtime.o'),('native-yhm-transport','native_yhm_transport.o'),('native-yhm-state','native_yhm_state.o'),('native-yhm-initialize','native_yhm_initialize.o'),('native-yhm-frontend','native_yhm_frontend.o'),('native-yhm-chip-id','native_yhm_chip_id.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 # Keep the source graph needed by write and handle discovery without importing
 # unrelated transport entry points merely because they share a source file.
 selected=out/'yhm-read-write-discovery.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_yhm_register_write_native','--undefined=r1_yhm_device_handles_initialize','--undefined=r1_yhm_chip_id_native',*map(str,objects[2:]),'-o',str(selected)],check=True)
 linked=out/'native-yhm-chip-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(objects[1]),str(selected),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert not set(['r1_gxt310_self_check','r1_device_preinitialize_3510c','r1_yhm_register_write_native','r1_yhm_device_handles_initialize','r1_rtt_delay_cycles','r1_yhm_chip_id_native','r1_yhm_register_read_native'])&set(u)
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 report=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},selected_yhm_object_sha256=sha(selected),linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,remaining_application_imports=[],application_imports_resolved=app,full_provider_graph_execution_verified=False,physical_sensor_or_delay_verified=False,application_linked=False,original_instruction_identity=False,gates=['Native YHM startup/chip ID and GXT self-check resolve source interfaces; GXT leaf providers remain.','Existing source YHM read/write, handle discovery, initialized state and delay are linked; read/logging remain fixtures in the chip-ID receipt.','The source void startup adapter intentionally discards the tested YHM uint32 return; sampled raw R0 is separately tested.','Full source startup graph, bus state, physical delay/sensors, raw ABI and byte-identical image remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('YHM chip ID and source read/write/discovery/state/delay linked;',len(u),'transitive startup imports remain')
if __name__=='__main__':main()
