#!/usr/bin/env python3
"""Link output operations with canonical configuration and actual string provider."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-hw-twi-wait-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-hw-twi-wait','native_hw_twi_wait.o',None),('native-hw-twi-completion-runtime','native-hw-twi-completion-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-hw-twi-wait-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 parent=json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols'];closed=sorted(set(parent)-set(u));assert closed==[] and not(set(u)-set(parent)) and len(u)==36
 cr=BASE/'native-hw-twi-registration/report.json';c=json.loads(cr.read_text());canonical=cr.parent/'native_hw_twi_registration-selected.o';assert sha(canonical)==c['units'][0]['object_sha256'];reports[str(cr.relative_to(BASE))]=sha(cr)
 for p,h in c['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 graph=out/'hw-wait-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_twi_primary_wait_adapter','-u','r1_twi_secondary_wait_adapter',str(objects[0]),str(canonical),'-o',str(graph)],check=True);objects.append(canonical)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,graph_object_sha256=sha(graph),graph_undefined_symbols=undefined_symbols(graph)[0],closed_parent_imports=closed,newly_exposed_imports=[],instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('TWI wait runtime:',len(u),'imports')
if __name__=='__main__':main()
