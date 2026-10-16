#!/usr/bin/env python3
"""Compose native identity reader, existing Nordic SVC and complete formatter."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-device-id-reader-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-device-id-reader','native_device_id_reader.o',None),('native-device-id-command-runtime','native-device-id-command-runtime.o','linked_sha256'),('native-formatter-runtime','native-formatter-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=out/'reader-helpers-source.o';roots=['memcpy','r1_advertising_controller_address_get'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(objects[1]),'-o',str(helpers)],check=True);assert undefined_symbols(helpers)[0]==[]
 graph=out/'device-id-reader-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(helpers),str(objects[2]),'-o',str(graph)],check=True);gu,gd=undefined_symbols(graph);assert gu==[]
 # Reuse the parent's integer-runtime owner; do not duplicate its definitions.
 leaf_paths={}
 for directory in ['native-formatter-engine','native-formatter-math','native-formatter-runtime']:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());reports[str(rp.relative_to(BASE))]=sha(rp)
  for name,h in r['objects'].items():
   if name.startswith(('native-formatter-core/','native-formatter-product/','native-formatter-add/','native-formatter-unsigned/','native-formatter-decimal/','native-formatter-output/','native-formatter-wrappers/')):assert sha(BASE/name)==h;leaf_paths[name]=h
 leaves=[BASE/p for p in leaf_paths];assert len(leaves)==7
 linked=out/'native-device-id-reader-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects[:2]+leaves),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old
 assert closed=={'r1_native_device_id_read_boundary','snprintf'} and new==set()
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects+leaves},graph_object_sha256=sha(graph),helper_object_sha256=sha(helpers),graph_undefined_symbols=gu,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),runtime_admission_changed=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Device ID reader runtime:',len(u),'imports;direct graph has',len(gu))
if __name__=='__main__':main()
