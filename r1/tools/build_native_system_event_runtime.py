#!/usr/bin/env python3
"""Compose system command bodies with actual header/response/encoder graph."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-system-event-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-system-event-commands','native_system_event_commands.o',None),('native-response-graph-runtime','native-response-graph-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=[]
 for directory,filename,root in [('native-health-commands','native_health_commands.o','r1_protocol_send_flag_set_c'),('native-protocol-ack','native_protocol_ack.o','r1_packet_field12_get')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/filename;assert sha(obj)==r['units'][0]['object_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
  p=out/(root+'.o');subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined='+root,str(obj),'-o',str(p)],check=True);helpers.append(p)
 graph_input=BASE/'native-response-graph-runtime/response-graph-source.o';assert sha(graph_input)==json.loads((graph_input.parent/'report.json').read_text())['graph_object_sha256']
 small=out/'system-event-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),*map(str,helpers),str(graph_input),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-system-event-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_protocol_command_000844ec','r1_protocol_command_00084860','r1_protocol_command_00084b24'} and not new
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects+[graph_input]},helpers={p.name:sha(p) for p in helpers},graph_object_sha256=sha(small),graph_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),whole_event_ble_or_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('System event runtime:',len(u),'imports;graph fixtures:',su)
if __name__=='__main__':main()
