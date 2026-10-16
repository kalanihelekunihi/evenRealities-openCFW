#!/usr/bin/env python3
"""Native DFU observer/auth with SDK type/helper; backend gates stay external."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-dfu-ble-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-dfu-ble-event','native_dfu_ble_event.o',None),('native-hw-twi-lifecycle-runtime','native-hw-twi-lifecycle-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 sr=BASE/'sdk-ble-service-common/report.json';sdk=json.loads(sr.read_text());row=sdk['units'][0];raw=sr.parent/'ble_srv_common.o';assert sha(raw)==row['object_sha256'];reports[str(sr.relative_to(BASE))]=sha(sr)
 for p,h in sdk['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helper=out/'indication-helper-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','ble_srv_is_indication_enabled',str(raw),'-o',str(helper)],check=True);assert undefined_symbols(helper)[0]==[]
 getter=out/'glasses-handle-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_glasses_connection_handle_get',str(objects[1]),'-o',str(getter)],check=True);assert undefined_symbols(getter)[0]==[]
 linked=out/'native-dfu-ble-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','--defsym=ble_dfu_buttonless_on_ble_evt=r1_native_dfu_ble_event',*map(str,objects),str(helper),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);parent=json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols'];closed=sorted(set(parent)-set(u));new=sorted(set(u)-set(parent));assert closed==['ble_dfu_buttonless_on_ble_evt','r1_ble_dfu_context'] and new==['r1_dfu_bootloader_prepare_boundary','r1_dfu_control_point_write_boundary'] and len(u)==28
 graph=out/'dfu-ble-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(helper),str(getter),'-o',str(graph)],check=True);objects.append(raw)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,helper_object_sha256=sha(helper),getter_object_sha256=sha(getter),graph_object_sha256=sha(graph),graph_undefined_symbols=undefined_symbols(graph)[0],closed_parent_imports=closed,newly_exposed_imports=new,native_observer_differs_from_sdk=True,complete_sdk_observer_substituted=False,source_context_bytes=28,new_value_seed_bytes=4,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native DFU observer/auth source runtime:',len(u),'imports;two explicit backend boundaries')
if __name__=='__main__':main()
