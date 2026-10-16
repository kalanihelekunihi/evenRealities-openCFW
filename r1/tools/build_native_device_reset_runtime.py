#!/usr/bin/env python3
"""Integrate device/reset bodies with available source startup providers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-device-reset-runtime';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);objects=[];providers={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name in [('native-device-reset-startup','native_device_reset_startup.o'),('native-startup-providers','native-startup-providers.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);objects.append(obj);providers[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-device-reset-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);unresolved,defined=undefined_symbols(linked)
 app_imports=json.loads((BASE/'native-application-entry/report.json').read_text())['units'][0]['undefined'];remaining=sorted(set(app_imports)&set(unresolved));assert remaining==['ble_dfu_buttonless_async_svci_init','cm_backtrace_init']
 assert {'r1_device_preinitialize_3510c','r1_gxt310_self_check','r1_reset_reason_decode_and_report'}<=set(unresolved)
 report=dict(status='source-compiled-device-reset-startup-integration-candidate',provider_reports=providers,objects={str(p.relative_to(BASE)):sha(p) for p in objects},inputs=inputs,linked_sha256=sha(linked),undefined_symbols=unresolved,defined_symbols=defined,application_imports_resolved=sorted(set(app_imports)-set(unresolved)),remaining_application_imports=remaining,full_provider_execution_verified=False,original_instruction_identity=False,application_linked=False,gates=['Eleven direct application imports now resolve to compiled source. Two direct imports and all transitive unresolved symbols remain explicit.','Device pre-initialization, sensor self-check and reset decode/report providers remain required source work.','Typed leaf fixtures, two-byte source noop equality and selected state tests are not full linked graph/raw ABI/physical MMIO or byte-identical image proof.'])
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Device/reset startup source linked;',len(app_imports)-len(remaining),'direct application imports resolved;',len(unresolved),'total imports remain')
if __name__=='__main__':main()
