#!/usr/bin/env python3
"""Add upstream CmBacktrace initialization and recovered bounds to source startup."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-cmbacktrace-runtime';out.mkdir(exist_ok=True);objects=[];providers={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-device-reset-runtime','native-device-reset-runtime.o'),('native-cmbacktrace-init','cmbacktrace-init-runtime.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==r['linked_sha256'];objects.append(obj);providers[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 config=ROOT/'r1/source-config/runtime/cmbacktrace/native-bounds.ld';inputs[str(config.relative_to(ROOT))]=sha(config)
 linked=out/'native-cmbacktrace-runtime.o';cmd=['arm-none-eabi-ld','-r','-T',str(config),*map(str,objects),'-o',str(linked)];subprocess.run(cmd,check=True);u,d=undefined_symbols(linked)
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];remaining=sorted(set(app)&set(u));assert remaining==['ble_dfu_buttonless_async_svci_init'];assert 'r1_retained_log_printf_sink' in u and not any(x.startswith('r1_cmb_') for x in u)
 report=dict(provider_reports=providers,objects={str(p.relative_to(BASE)):sha(p) for p in objects},inputs=inputs,command=cmd,linked_sha256=sha(linked),undefined_symbols=u,defined_symbols=d,application_imports_resolved=sorted(set(app)-set(u)),remaining_application_imports=remaining,full_provider_execution_verified=False,application_linked=False,original_instruction_identity=False,gates=['Twelve direct application imports resolve to compiled source; DFU SVC initialization and transitive providers remain.','Recovered CMB bounds are source-owned symbol configuration, not complete image placement.','Only CMB initialization is native-tested; fault/unwind adapters, retained logger and full graph/raw ABI/image identity remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('CmBacktrace startup linked:',len(app)-len(remaining),'direct imports resolved;',len(u),'total unresolved')
if __name__=='__main__':main()
