#!/usr/bin/env python3
"""Compose payload getter and the complete currently implemented crash providers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-crash-payload-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-health-cache-runtime','native-health-cache-runtime.o','linked_sha256'),('native-crash-payload','native_crash_payload.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-crash-payload-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True)
 u,d=undefined_symbols(linked);old=undefined_symbols(objects[0])[0];assert sorted(set(old)-set(u))==['r1_crash_record_marker_set'] and sorted(set(u)-set(old))==[] and len(u)==23
 graph=out/'crash-initialize-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_health_crash_record_initializer',str(linked),'-o',str(graph)],check=True);assert undefined_symbols(graph)[0]==[]
 r=dict(graph_object_sha256=sha(graph),inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=['r1_crash_record_marker_set'],newly_exposed_imports=[],canonical_reset_context_reused=True,composed_runtime_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Crash payload getter linked:23 imports')
if __name__=='__main__':main()
