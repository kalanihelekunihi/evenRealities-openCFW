#!/usr/bin/env python3
"""Compose callbacks with existing source cluster and pinned CMSIS state getter."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-hw-twi-completion-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-hw-twi-completion','native_hw_twi_completion.o',None),('native-peripheral-bindings-runtime','native-peripheral-bindings-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 rp=BASE/'rtos-semaphore-new/report.json';r=json.loads(rp.read_text());cmsis=rp.parent/'cmsis_os2.o';row=next(x for x in r['units'] if x['source'].endswith('cmsis_os2.c'));assert sha(cmsis)==row['object_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp)
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 kernel=out/'kernel-state-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','osKernelGetState',str(cmsis),'-o',str(kernel)],check=True);assert undefined_symbols(kernel)[0]==['xTaskGetSchedulerState']
 linked=out/'native-hw-twi-completion-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),str(kernel),'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 parent=json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols'];closed=sorted(set(parent)-set(u));assert closed==['r1_hw_twi0_irq','r1_hw_twi1_irq'] and not(set(u)-set(parent)) and len(u)==36
 # Focused graph leaves scheduler/semaphore calls as explicit verification seams.
 rp=BASE/'native-hw-twi-registration/report.json';r=json.loads(rp.read_text());canonical=rp.parent/'native_hw_twi_registration-selected.o';assert sha(canonical)==r['units'][0]['object_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp)
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 graph=out/'hw-completion-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_hw_twi0_irq','-u','r1_hw_twi1_irq',str(objects[0]),str(canonical),str(kernel),'-o',str(graph)],check=True)
 objects += [cmsis,canonical]
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,kernel_object_sha256=sha(kernel),graph_object_sha256=sha(graph),graph_undefined_symbols=undefined_symbols(graph)[0],closed_parent_imports=closed,newly_exposed_imports=[],cmsis_kernel_state_source_bytes=4,canonical_kernel_state_final_placement_proven=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('TWI completion source runtime:',len(u),'imports')
if __name__=='__main__':main()
