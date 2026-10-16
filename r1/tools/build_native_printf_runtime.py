#!/usr/bin/env python3
"""Select existing printf/RTT wrapper bodies into the main partial graph."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-printf-runtime';out.mkdir(exist_ok=True)
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-dfu-backend-runtime','native-dfu-backend-runtime.o','linked_sha256'),('native-formatter-stream','native_formatter_stream.o',None),('native-rtt-write','native_rtt_write.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name
  assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256'])
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
  reports[str(rp.relative_to(BASE))]=sha(rp);objects.append(obj)
 selected=out/'printf-source.o'
 subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','printf',*map(str,objects[1:]),'-o',str(selected)],check=True)
 u,d=undefined_symbols(selected)
 assert set(u)=={'r1_format_core','SEGGER_RTT_Init','SEGGER_RTT_WriteNoLock','_SEGGER_RTT'}
 linked=out/'native-printf-runtime.o'
 subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(selected),'-o',str(linked)],check=True)
 unresolved,defined=undefined_symbols(linked);old=undefined_symbols(objects[0])[0]
 assert sorted(set(old)-set(unresolved))==['printf'] and not(set(unresolved)-set(old)) and len(unresolved)==24
 receipts={str((BASE/p).relative_to(BASE)):sha(BASE/p) for p in ['native-formatter-stream/verification.json','native-rtt-write/verification.json']}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},existing_verification_receipts=receipts,selected_sha256=sha(selected),selected_undefined_symbols=u,selected_defined_symbols=d,linked_sha256=sha(linked),undefined_symbols=unresolved,closed_parent_imports=['printf'],newly_exposed_imports=[],existing_formatter_and_rtt_state_reused=True,new_source_bodies=False,composed_runtime_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False,gates=['Existing bounded printf and RTT leaf receipts do not establish composed application execution, private-frame history, interrupt/debugger behavior or whole-image identity.','Retained logging sink remains unresolved; printf is a separate provider.'])
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Existing printf/RTT bodies integrated:24 imports, no duplicate state')
if __name__=='__main__':main()
