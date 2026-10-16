#!/usr/bin/env python3
"""Extend startup with actual command tables/dispatchers and available handler bodies."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-health-commands-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 specs=[('native-protocol-reset-port-runtime','native-protocol-reset-port-runtime.o','linked_sha256'),('native-health-commands','native_health_commands.o',None),('native-protocol-modules','native_protocol_modules.o',None),('native-protocol-device-info','native_protocol_device_info.o',None),('native-protocol-device-status','native_protocol_device_status.o',None),('native-protocol-event-handlers','native_protocol_event_handlers.o',None)]
 for directory,name,key in specs:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 selected=out/'health-dispatch-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_health_registration_dispatcher',str(objects[2]),'-o',str(selected)],check=True)
 graph=out/'health-dispatch-graph-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(selected),str(objects[1]),str(objects[5]),'-o',str(graph)],check=True);gu,gd=undefined_symbols(graph);assert gu==['r1_event_publish','r1_protocol_send_response','r1_service_health_report_set']
 linked=out/'native-health-commands-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 parent=json.loads((BASE/'native-protocol-reset-port-runtime/report.json').read_text());old=set(parent['undefined_symbols']);assert not {'r1_ble_event_dispatch','r1_eus_system_dispatch_plan_build','r1_health_registration_dispatcher'}&set(u)
 r=dict(graph_object_sha256=sha(graph),graph_undefined_symbols=gu,selected_dispatch_object_sha256=sha(selected),inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(old-set(u)),newly_exposed_imports=sorted(set(u)-old),all_three_dispatchers_source_linked=True,whole_dispatch_graph_executed=False,whole_startup_graph_executed=False,full_cross_translation_unit_callback_types_verified=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Health command/dispatch source bundle:',len(u),'imports;',len(r['closed_parent_imports']),'parent imports closed;',len(r['newly_exposed_imports']),'new leaf/data dependencies')
if __name__=='__main__':main()
