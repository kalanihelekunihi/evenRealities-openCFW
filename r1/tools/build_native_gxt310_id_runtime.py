#!/usr/bin/env python3
"""Link native GXT ID providers into self-check and larger source startup graphs."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-gxt310-id-runtime';out.mkdir(exist_ok=True);reports={};objects=[];inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-gxt310-id','native_gxt310_id.o'),('native-yhm-chip-runtime','native-yhm-chip-runtime.o'),('native-device-checks','native_device_checks.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 selected=out/'gxt-selfcheck-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_gxt310_self_check',str(objects[0]),str(objects[2]),'-o',str(selected)],check=True);su,sd=undefined_symbols(selected)
 assert len(su)==8 and not {'r1_gxt310_chip_id_channel0','r1_gxt310_chip_id_channel2'}&set(su)
 linked=out/'native-gxt310-id-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(objects[1]),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert 'r1_gxt310_register_read_native' in u and not {'r1_gxt310_chip_id_channel0','r1_gxt310_chip_id_channel2'}&set(u)
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 report=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},selfcheck_object_sha256=sha(selected),selfcheck_undefined_symbols=su,selfcheck_defined_symbols=sd,linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,remaining_application_imports=[],application_imports_resolved=app,whole_startup_graph_executed=False,physical_sensor_verified=False,application_linked=False,original_instruction_identity=False,gates=['Both GXT ID veneers and their shared reader now link as source; the lower register-read provider remains unresolved.','Source self-check graph contains both actual ID providers, with bus/enable/disable/read/logging leaves external.','Full startup graph, physical sensor/bus, raw private frames, source data/state placement and byte-identical image remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('GXT ID source linked;',len(u),'startup transitive imports remain;',len(su),'self-check graph imports')
if __name__=='__main__':main()
