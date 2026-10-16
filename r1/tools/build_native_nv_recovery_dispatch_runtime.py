#!/usr/bin/env python3
"""Compose native dispatcher while retaining separate merge/report admission gates."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-nv-recovery-dispatch-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-nv-recovery-dispatch','native_nv_recovery_dispatch.o',None),('native-nv-recovery-envelope-runtime','native-nv-recovery-envelope-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 oldgraph=objects[1].parent/'nv-recovery-envelope-source.o';assert sha(oldgraph)==json.loads((oldgraph.parent/'report.json').read_text())['envelope_object_sha256'];graph=out/'nv-recovery-dispatch-graph-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(oldgraph),'-o',str(graph)],check=True);gu,gd=undefined_symbols(graph)
 linked=out/'native-nv-recovery-dispatch-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_native_nv_recovery_command_dispatch'} and new=={'r1_native_nv_recovery_merge_boundary','r1_native_nv_recovery_report_boundary'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects+[oldgraph]},graph_object_sha256=sha(graph),graph_undefined_symbols=gu,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),bounded_planner_modified=False,merge_and_identity_report_effects_implemented=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Build-only dispatcher runtime:',len(u),'imports;merge/report remain unresolved')
if __name__=='__main__':main()
