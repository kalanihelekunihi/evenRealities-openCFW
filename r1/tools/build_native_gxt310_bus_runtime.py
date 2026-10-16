#!/usr/bin/env python3
"""Integrate source GXT bus/cache/request providers with available startup source."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-gxt310-bus-runtime';out.mkdir(exist_ok=True);reports={};objects=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-gxt310-bus','native_gxt310_bus.o'),('native-gxt310-id-runtime','native-gxt310-id-runtime.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-gxt310-bus-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 assert not {'r1_i2c2_handle_cache','r1_gxt310_bus_acquire','r1_gxt310_bus_release','r1_gxt310_register_read_native','r1_gxt310_register_write_native'}&set(u)
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 report=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,remaining_application_imports=[],application_imports_resolved=app,whole_startup_graph_executed=False,physical_i2c_verified=False,application_linked=False,original_instruction_identity=False,gates=['GXT cached I2C handle, lock/unlock and read/write request providers now resolve to source.','Existing source registry/dispatch and cold C state are linked; body receipt uses named registry/dispatch fixtures.','GXT mode enable/disable and other transitive providers remain unresolved.','Physical bus, full startup graph, raw ABI and final source state/link placement and image identity remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('GXT bus/cache/read/write source linked;',len(u),'transitive startup imports remain')
if __name__=='__main__':main()
