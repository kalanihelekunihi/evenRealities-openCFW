#!/usr/bin/env python3
"""Link output operations with canonical configuration and actual string provider."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-output-gpio-operations-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-output-gpio-operations','native_output_gpio_operations.o',None),('native-output-gpio-runtime','native-output-gpio-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-output-gpio-operations-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 parent=json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols'];closed=sorted(set(parent)-set(u));assert closed==['r1_output_gpio_driver14','r1_output_gpio_slot10','r1_output_gpio_slot1c'] and not(set(u)-set(parent)) and len(u)==45
 graph=out/'output-operations-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_output_gpio_slot1c','-u','r1_output_gpio_slot10','-u','r1_output_gpio_driver14',str(linked),'-o',str(graph)],check=True)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,graph_object_sha256=sha(graph),graph_undefined_symbols=undefined_symbols(graph)[0],closed_parent_imports=closed,newly_exposed_imports=[],instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('GPIO operations runtime:',len(u),'imports')
if __name__=='__main__':main()
