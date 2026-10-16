#!/usr/bin/env python3
"""Link mode control with source GXT bus/ID/self-check and larger startup bundle."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-gxt310-mode-runtime';out.mkdir(exist_ok=True);reports={};objects=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-gxt310-mode','native_gxt310_mode.o'),('native-gxt310-bus-runtime','native-gxt310-bus-runtime.o'),('native-gxt310-bus','native_gxt310_bus.o'),('native-gxt310-id','native_gxt310_id.o'),('native-device-checks','native_device_checks.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 selected=out/'gxt-control-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_gxt310_self_check','--undefined=r1_i2c2_handle_cache',str(objects[0]),*map(str,objects[2:]),'-o',str(selected)],check=True);su,sd=undefined_symbols(selected)
 assert len(su)==10 and not any(x.startswith('r1_gxt310_') for x in su)
 linked=out/'native-gxt310-mode-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(objects[1]),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert not any(x.startswith('r1_gxt310_') for x in u)
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 report=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},control_object_sha256=sha(selected),control_undefined_symbols=su,control_defined_symbols=sd,linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,remaining_application_imports=[],application_imports_resolved=app,whole_startup_graph_executed=False,physical_sensor_verified=False,application_linked=False,original_instruction_identity=False,gates=['Source self-check, mode/pair controls, both channel ID providers and bus/cache/request bodies are selected together.','Registry lookup/dispatch and logging remain external in the selected GXT control subgraph; larger startup links available registry/logger source.','Full startup execution, physical sensors, raw ABI/private frames and data/state/link placement and original byte-identical image remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('All named GXT providers source-linked;',len(u),'startup transitive imports;',len(su),'registry/logging control-subgraph imports')
if __name__=='__main__':main()
