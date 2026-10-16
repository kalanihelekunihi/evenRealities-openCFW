#!/usr/bin/env python3
"""Join registered battery bodies with source-owned, shared cold context slices."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
MODULES=['native-battery-runtime','native-battery-control','native-battery-statistics','native-battery-filter','native-battery-cadence','native-battery-configuration','native-battery-discharge','native-battery-initial-curve','native-battery-recovery','native-battery-diagnostic','native-battery-low','native-battery-voltage','native-charger-state','native-battery-frame','native-kv-device-fields','native-yhm-system-track','native-battery-protocol','native-yhm-status']
def main():
 out=BASE/'native-battery-context-runtime';out.mkdir(exist_ok=True);source=ROOT/'r1/components/runtime/native_battery_context_config.c';cfg=out/'native_battery_context_config.o';dep=out/'native_battery_context_config.d';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-fshort-enums','-std=c11','-Os','-ffreestanding','-fno-builtin','-fdata-sections','-Wall','-Wextra','-Werror','-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(cfg)];subprocess.run(cmd,check=True)
 layout=ROOT/'r1/source-config/runtime/native_battery_context_composition.ld';inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(layout.relative_to(ROOT)):sha(layout)}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(p);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
 reports={};objects=[]
 for name in MODULES+['native-status-ring-runtime']:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());obj=rp.parent/('native-status-ring-runtime.o' if name=='native-status-ring-runtime' else Path(r['units'][0]['source']).stem+'.o');assert sha(obj)==(r['linked_sha256'] if name=='native-status-ring-runtime' else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 trp=BASE/'rtos-ticks/report.json';tr=json.loads(trp.read_text());tu=next(x for x in tr['units'] if 'osKernelGetTickFreq' in x['defined']);to=Path(tu['command'][-1]);assert sha(to)==tu['object_sha256'];reports[str(trp.relative_to(BASE))]=sha(trp)
 for p,h in tr['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 tick=out/'cmsis-tick-frequency-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=osKernelGetTickFreq',str(to),'-o',str(tick)],check=True);assert not undefined_symbols(tick)[0]
 linked=out/'native-battery-context-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','-T',str(layout),str(cfg),str(tick),*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked)
 owners=out/'context-existing-owners.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in ['r1_device_state_byte_2c','r1_device_state_byte_2d','r1_vbat_adc_device']],str(objects[-1]),'-o',str(owners)],check=True)
 small=out/'battery-control-context-source.o';subprocess.run(['arm-none-eabi-ld','-r','-T',str(layout),str(cfg),str(owners),*map(str,objects[:3]),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 old=set(json.loads((BASE/'native-status-ring-runtime/report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},config_object_sha256=sha(cfg),cmsis_tick_frequency_object_sha256=sha(tick),cmsis_input_object_sha256=sha(to),existing_owners_sha256=sha(owners),control_object_sha256=sha(small),control_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),source_contexts_with_existing_alias_owners=True,whole_battery_hardware_or_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Battery context runtime:',len(u),'imports;',len(closed),'closed;',len(new),'new',sorted(new))
if __name__=='__main__':main()
