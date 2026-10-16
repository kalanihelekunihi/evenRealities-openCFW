#!/usr/bin/env python3
"""Link output operations with canonical configuration and actual string provider."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-peripheral-bindings-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-peripheral-bindings','native_peripheral_bindings.o',None),('native-output-gpio-lifecycle-runtime','native-output-gpio-lifecycle-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-peripheral-bindings-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 parent=json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols'];closed=sorted(set(parent)-set(u));assert closed==['r1_led_ldo_device_bind','r1_motion_interrupt_input_lookup','r1_ppg_device_bind','r1_touch_device_bind'] and not(set(u)-set(parent)) and len(u)==38
 graph=out/'peripheral-bindings-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_motion_bus_device_bind','-u','r1_led_ldo_device_bind','-u','r1_motion_interrupt_input_lookup','-u','r1_ppg_device_bind','-u','r1_touch_device_bind',str(linked),'-o',str(graph)],check=True)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,graph_object_sha256=sha(graph),graph_undefined_symbols=undefined_symbols(graph)[0],closed_parent_imports=closed,newly_exposed_imports=[],instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Peripheral bindings runtime:',len(u),'imports')
if __name__=='__main__':main()
