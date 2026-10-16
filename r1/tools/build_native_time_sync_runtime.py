#!/usr/bin/env python3
"""Compose build-only time synchronization command with authenticated parents."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-time-sync-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-time-sync-command','native_time_sync_command.o',None),('native-nv-recovery-dispatch-runtime','native-nv-recovery-dispatch-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 accessor=out/'accessor-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_packet_field12_get',str(objects[1]),'-o',str(accessor)],check=True);assert undefined_symbols(accessor)[0]==[]
 graph=out/'time-sync-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(accessor),'-o',str(graph)],check=True);gu,gd=undefined_symbols(graph)
 linked=out/'native-time-sync-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old
 assert closed=={'r1_protocol_command_000846dc'} and new=={'r1_protocol_time_timeout_callback','r1_nv_recovery_needed_query_boundary'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},graph_object_sha256=sha(graph),accessor_object_sha256=sha(accessor),graph_undefined_symbols=gu,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),runtime_admission_changed=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Build-only time synchronization runtime:',len(u),'imports')
if __name__=='__main__':main()
