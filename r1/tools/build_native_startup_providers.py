#!/usr/bin/env python3
"""Link available source startup/board providers without hiding remaining imports."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-startup-providers';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};objects=[];providers={};all_defined=set();all_unresolved=set()
 for directory,name in [('native-application-startup-runtime','native-application-startup-runtime.o'),('native-peripheral-module','native_peripheral_module.o'),('board','native-board.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r.get('relocatable_sha256') or r['units'][0]['object_sha256'])
  for p,h in r.get('inputs',{}).items():assert sha(ROOT/p)==h,p;inputs[p]=h
  providers[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj);u,d=undefined_symbols(obj);all_unresolved.update(u);all_defined.update(d)
 board=json.loads((BASE/'board/report.json').read_text());assert board['input_reports']['native-initcalls/report.json']==sha(BASE/'native-initcalls/report.json')
 config=ROOT/'r1/source-config/startup/native-provider-aliases.json';aliases=json.loads(config.read_text());assert aliases=={'r1_boot_ctor_run':'r1_native_boot_initcall_dispatch'};assert all(target in all_defined and alias not in all_defined for alias,target in aliases.items());inputs[str(config.relative_to(ROOT))]=sha(config)
 linked=out/'native-startup-providers.o';command=['arm-none-eabi-ld','-r',*['--defsym='+alias+'='+target for alias,target in aliases.items()],*map(str,objects),'-o',str(linked)];subprocess.run(command,check=True);unresolved,defined=undefined_symbols(linked);assert set(unresolved)==all_unresolved-all_defined-set(aliases)
 symbols={v[2]:int(v[0],16) for line in subprocess.check_output(['arm-none-eabi-nm',str(linked)],text=True).splitlines() if len(v:=line.split())==3};assert all(symbols[alias]==symbols[target] for alias,target in aliases.items())
 app=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];closed=sorted(set(app)-set(unresolved));remaining_app=sorted(set(app)&set(unresolved));assert len(closed)==9 and remaining_app==['ble_dfu_buttonless_async_svci_init','cm_backtrace_init','r1_device_module_init','r1_reset_reason_nordic_adapter']
 report=dict(status='source-compiled-startup-provider-integration-candidate',command=command,provider_reports=providers,objects={str(p.relative_to(BASE)):sha(p) for p in objects},inputs=inputs,source_aliases=aliases,linked_sha256=sha(linked),undefined_symbols=unresolved,defined_symbols=defined,application_imports_resolved=closed,remaining_application_imports=remaining_app,full_provider_execution_verified=False,original_instruction_identity=False,application_linked=False,gates=['Nine direct application imports resolve to compiled source; four direct imports and all transitive board/peripheral imports remain explicit.','Alias identifies the already compiled and verified constructor C body; it does not claim instruction/placement equality.','Typed fixture tests are not execution of this complete linked graph. Startup raw ABI, source-owned initialization/callback, hardware and byte-identical image integration remain open.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Available source startup providers linked;',len(closed),'application imports resolved;',len(unresolved),'total imports remain')
if __name__=='__main__':main()
