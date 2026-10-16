#!/usr/bin/env python3
"""Link actual source vector setup into DFU and the larger startup candidates."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-dfu-vector-runtime';out.mkdir(exist_ok=True);reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};objects={}
 for directory,name in [('native-dfu-vector-set','native-dfu-vector-set.o'),('native-dfu-svci-init','native-dfu-svci-init.o'),('native-dfu-startup-runtime','native-dfu-startup-runtime.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==r['linked_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp);objects[directory]=obj
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 dfu=out/'native-dfu-vector-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects['native-dfu-vector-set']),str(objects['native-dfu-svci-init']),'-o',str(dfu)],check=True);du,dd=undefined_symbols(dfu);assert du==['nrf_log_frontend_std_0','nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get']
 startup=out/'native-vector-startup-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects['native-dfu-vector-set']),str(objects['native-dfu-startup-runtime']),'-o',str(startup)],check=True);u,d=undefined_symbols(startup);assert 'nrf_dfu_svci_vector_table_set' not in u
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects.values()},linked_sha256=sha(startup),undefined_symbols=u,defined_symbols=d,dfu_runtime_sha256=sha(dfu),dfu_undefined_symbols=du,dfu_defined_symbols=dd,remaining_application_imports=[],application_imports_resolved=app,full_provider_graph_execution_verified=False,physical_supervisor_verified=False,application_linked=False,original_instruction_identity=False,gates=['DFU source entry, set and restore are available as one graph; actual SVC handlers and hardware remain external.','All13 direct startup imports resolve; transitive unresolved imports are retained.','Full startup graph execution, raw ABI/private state, original compiler/link placement and whole-image byte identity remain open.'])
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('DFU source graph has4 logging imports; all13 direct app imports source-linked;',len(u),'transitive imports remain')
if __name__=='__main__':main()
