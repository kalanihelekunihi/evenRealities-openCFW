#!/usr/bin/env python3
"""Link all thirteen direct application startup imports to available C source."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-dfu-startup-runtime';out.mkdir(exist_ok=True);objects=[];providers={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-cmbacktrace-runtime','native-cmbacktrace-runtime.o'),('native-dfu-svci-init','native-dfu-svci-init.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==r['linked_sha256'];objects.append(obj);providers[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-dfu-startup-runtime.o';cmd=['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)];subprocess.run(cmd,check=True);u,d=undefined_symbols(linked)
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];assert not set(app)&set(u);assert 'nrf_dfu_svci_vector_table_set' in u
 report=dict(provider_reports=providers,objects={str(p.relative_to(BASE)):sha(p) for p in objects},inputs=inputs,command=cmd,linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,application_imports_resolved=sorted(app),remaining_application_imports=[],full_provider_execution_verified=False,application_linked=False,original_instruction_identity=False,gates=['All thirteen direct application imports now resolve to compiled source; all transitive unresolved imports are retained.','SVC0/SVC19 architectural bridges compile, but their actual supervisor handlers and hardware behavior remain unverified.','Vector-to-bootloader setter, retained logger and other leaf providers remain source work.','Typed per-body fixture verification does not prove full linked-provider execution, raw ABI, original placement or byte-identical firmware.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('All13 direct app imports source-linked;',len(u),'transitive imports remain')
if __name__=='__main__':main()
