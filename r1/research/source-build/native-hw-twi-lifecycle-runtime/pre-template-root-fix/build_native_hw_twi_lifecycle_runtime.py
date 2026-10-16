#!/usr/bin/env python3
"""Consolidate legacy-init and TWIM state from existing source leaves."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-hw-twi-lifecycle-runtime';out.mkdir(exist_ok=True);objects={};reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for key,directory,name,field in [('life','native-hw-twi-lifecycle','native_hw_twi_lifecycle.o',None),('ops','native-hw-twi-operations','native_hw_twi_operations.o',None),('register','native-hw-twi-register','native_hw_twi_register.o',None),('base','native-hw-twi-wait-runtime','native-hw-twi-wait-runtime.o','linked_sha256'),('twim','sdk-twim','nrfx_twim.o',None),('legacy','sdk-legacy-twi','nrf_drv_twi.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[field] if field else r['units'][0]['object_sha256']);objects[key]=obj;reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 sdk=out/'twim-legacy-consolidated-source.o';roots=['nrf_drv_twi_init','nrfx_twim_init','nrfx_twim_tx','nrfx_twim_rx','nrfx_twim_enable','nrfx_twim_disable','nrfx_twim_uninit'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*sum([['-u',n] for n in roots],[]),str(objects['twim']),str(objects['legacy']),'-o',str(sdk)],check=True);assert undefined_symbols(sdk)[0]==[]
 # Recompose from the pre-TWIM parent; do not add a second m_cb beside the older
 # TX/RX-only selection embedded in subsequent historical runtime objects.
 linked=out/'native-hw-twi-lifecycle-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,[objects[k] for k in ['life','ops','register','base']]),str(sdk),'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 old=BASE/'native-hw-twi-operations-runtime/report.json';oldr=json.loads(old.read_text());reports[str(old.relative_to(BASE))]=sha(old);closed=sorted(set(oldr['undefined_symbols'])-set(u));assert closed==['r1_hw_twi0_close','r1_hw_twi0_open','r1_hw_twi1_close','r1_hw_twi1_open'] and not(set(u)-set(oldr['undefined_symbols'])) and len(u)==28
 cr=BASE/'native-hw-twi-registration/report.json';c=json.loads(cr.read_text());canonical=cr.parent/'native_hw_twi_registration-selected.o';assert sha(canonical)==c['units'][0]['object_sha256'];reports[str(cr.relative_to(BASE))]=sha(cr)
 for p,h in c['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 graph=out/'hw-lifecycle-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*sum([['-u',n] for n in closed],[]),str(objects['life']),str(canonical),'-o',str(graph)],check=True);objects['canonical']=canonical
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects.values()},composition_roles={k:str(p.relative_to(BASE)) for k,p in objects.items()},linked_sha256=sha(linked),undefined_symbols=u,sdk_object_sha256=sha(sdk),graph_object_sha256=sha(graph),graph_undefined_symbols=undefined_symbols(graph)[0],closed_parent_imports=closed,newly_exposed_imports=[],single_twim_family_from_pre_twim_parent=True,legacy_sdk_source_unchanged=True,sdk_control_block_native_identity_verified=False,sdk_hardware_transfer_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Consolidated TWI lifecycle runtime:',len(u),'imports;one SDK family')
if __name__=='__main__':main()
