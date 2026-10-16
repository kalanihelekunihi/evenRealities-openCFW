#!/usr/bin/env python3
"""Compose native touch handler without changing portable planner admission."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-touch-switch-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-touch-switch','native_touch_switch.o',None),('native-device-id-reader-runtime','native-device-id-reader-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=out/'touch-switch-helpers-source.o';roots=['r1_packet_field12_get'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(objects[1]),'-o',str(helpers)],check=True);assert undefined_symbols(helpers)[0]==[]
 rp=BASE/'native-protocol-serial/report.json';r=json.loads(rp.read_text());serial=rp.parent/'native_protocol_serial.o';assert sha(serial)==r['units'][0]['object_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp)
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 checked=out/'touch-checked-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_protocol_send_checked',str(serial),'-o',str(checked)],check=True)
 graph=out/'touch-switch-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(helpers),str(checked),'-o',str(graph)],check=True);gu,gd=undefined_symbols(graph)
 linked=out/'native-touch-switch-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','--defsym=r1_touch_switch_handler_plan_decode=r1_native_touch_switch_handler',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old
 assert closed=={'r1_touch_switch_handler_plan_decode'} and new=={'r1_service_touch_open','r1_service_touch_close'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},graph_object_sha256=sha(graph),helper_object_sha256=sha(helpers),checked_object_sha256=sha(checked),serial_object_sha256=sha(serial),graph_undefined_symbols=gu,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),runtime_admission_changed=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native touch-switch runtime:',len(u),'imports')
if __name__=='__main__':main()
