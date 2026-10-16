#!/usr/bin/env python3
"""Compose touch client services and actual command caller; release stays gated."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-touch-services-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-touch-services','native_touch_services.o',None),('native-touch-switch-runtime','native-touch-switch-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 caller=objects[1].parent/'touch-switch-source.o';assert sha(caller)==json.loads((caller.parent/'report.json').read_text())['graph_object_sha256']
 graph=out/'touch-services-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(caller),'-o',str(graph)],check=True);gu,gd=undefined_symbols(graph)
 linked=out/'native-touch-services-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old
 assert closed=={'r1_service_touch_open','r1_service_touch_close'} and new=={'r1_touch_synthetic_release_boundary'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects+[caller]},graph_object_sha256=sha(graph),graph_undefined_symbols=gu,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),portable_planner_modified=False,runtime_admission_changed=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Touch services runtime:',len(u),'imports;release remains unresolved')
if __name__=='__main__':main()
