#!/usr/bin/env python3
"""Compose YHM transport/frontend/handle initialization with canonical providers and owned state."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-yhm-stage';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=True);vp=OUT/'verification.json';vp.unlink(missing_ok=True);rp=BASE/'board/report.json';board=json.loads(rp.read_text());bo=rp.parent/'native-board.o';assert sha(bo)==board['relocatable_sha256'];objects=[bo];reports={'board/report.json':sha(rp)}
 for module in ('transport','frontend','initialize','state'):
  name='native-yhm-'+module;report=BASE/name/'report.json';r=json.loads(report.read_text());obj=report.parent/(name.replace('-','_')+'.o');assert sha(obj)==r['units'][0]['object_sha256']
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
  objects.append(obj);reports[name+'/report.json']=sha(report)
 for name in ('native-yhm-status','native-charger-state','native-yhm-system-track'):
  report=BASE/name/'report.json';r=json.loads(report.read_text());obj=report.parent/(name.replace('-','_')+'.o');assert sha(obj)==r['units'][0]['object_sha256']
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p
  objects.append(obj);reports[name+'/report.json']=sha(report)
 state_receipt=BASE/'native-yhm-state/verification.json';state=json.loads(state_receipt.read_text());assert state['comparisons']==4 and state['object_sha256']==sha(BASE/'native-yhm-state/native_yhm_state.o')
 obj=OUT/'yhm-stage.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(obj)],check=True,capture_output=True);remaining,defined=undefined_symbols(obj);assert set(remaining)==set(board['remaining_symbols'])
 required={'r1_stacmd','r1_yhm_transport_context','r1_yhm_request','r1_yhm_ready_native','r1_yhm_register_read_native','r1_yhm_register_write_native','r1_yhm_device_handles_initialize','r1_yhm_status_native','r1_native_charger_state_get','r1_yhm_system_track_native','r1_native_charger_initialize'};assert required.issubset(defined)
 lines=subprocess.check_output(['arm-none-eabi-nm',str(obj)],text=True).splitlines()
 for name in ('r1_stacmd','r1_yhm_transport_context','r1_yhm_request'):assert sum(len(l.split())==3 and l.split()[-1]==name for l in lines)==1
 vp.write_text(json.dumps(dict(provider_reports=reports,objects={str(p.relative_to(ROOT)):sha(p) for p in objects},stage_object_sha256=sha(obj),driver_sha256=sha(Path(__file__)),state_verification_sha256=sha(state_receipt),shared_stacmd_header_sha256=sha(ROOT/'r1/components/board/native_stacmd.h'),remaining_symbols=remaining,new_unresolved_symbols=[],required_defined_symbols=sorted(required),canonical_board_integrated=False,application_linked=False,instruction_identity=False,limitations=['Relocatable source composition; executable YHM transport/state/provider graph still required','Readiness uses canonical STACMD configuration; context/request have verified cold storage','Warm-reset lifecycle, full startup and original whole-image instruction/byte identity remain open','Physical GPIO/transport timing/concurrency and complete firmware behavior unproven']),indent=2)+'\n');print('YHM stage:',len(remaining),'unresolved canonical symbols; no new dependency')
if __name__=='__main__':main()
