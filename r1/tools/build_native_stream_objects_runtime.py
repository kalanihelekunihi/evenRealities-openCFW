#!/usr/bin/env python3
"""Compose stream object core in preparation for singleton/registration providers."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-stream-objects-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-stream-poll-runtime','native-stream-poll-runtime.o','linked_sha256'),('native-stream-objects','native_stream_objects.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-stream-objects-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True)
 u,d=undefined_symbols(linked);old=undefined_symbols(objects[0])[0];assert sorted(set(old)-set(u))==[] and sorted(set(u)-set(old))==[] and len(u)==21
 graph=out/'stream-objects-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[arg for root in ['r1_stream_object_create','r1_stream_object_insert','r1_stream_object_lookup','r1_stream_object_flag_set'] for arg in ['-u',root]],str(linked),'-o',str(graph)],check=True);gu=undefined_symbols(graph)[0];assert set(gu)<=set(u)
 r=dict(graph_object_sha256=sha(graph),graph_undefined_symbols=gu,inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=[],newly_exposed_imports=[],canonical_reset_context_reused=True,composed_runtime_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Stream object core linked:21 imports;no provider fixtures in main graph')
if __name__=='__main__':main()
