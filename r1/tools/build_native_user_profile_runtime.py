#!/usr/bin/env python3
"""Compose native profile command with actual accessor/ack providers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-user-profile-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-user-profile-command','native_user_profile_command.o',None),('native-health-settings-runtime','native-health-settings-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=out/'profile-accessor-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_packet_field12_get',str(objects[1]),'-o',str(helpers)],check=True);assert undefined_symbols(helpers)[0]==[]
 rp=BASE/'native-health-commands/report.json';r=json.loads(rp.read_text());ack=rp.parent/'native_health_commands.o';assert sha(ack)==r['units'][0]['object_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp)
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 selected=out/'profile-flag-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_protocol_send_flag_set_c',str(ack),'-o',str(selected)],check=True)
 graph=out/'user-profile-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(helpers),str(selected),'-o',str(graph)],check=True);gu,gd=undefined_symbols(graph)
 linked=out/'native-user-profile-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','--defsym=r1_user_profile_handler=r1_native_user_profile_handler',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old
 assert closed=={'r1_user_profile_handler'} and new==set()
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects+[ack]},accessor_object_sha256=sha(helpers),ack_object_sha256=sha(selected),graph_object_sha256=sha(graph),graph_undefined_symbols=gu,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),portable_planner_modified=False,runtime_admission_changed=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Native user-profile runtime:',len(u),'imports')
if __name__=='__main__':main()
