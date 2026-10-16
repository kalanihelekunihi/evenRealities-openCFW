#!/usr/bin/env python3
"""Reuse the source time backend and integer division for daily metadata."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-daily-metadata-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name in [('native-daily-metadata','native_daily_metadata.o'),('native-vbat-cache-runtime','native-vbat-cache-runtime.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 registry=out/'time-provider-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_time_backend_timestamp','--undefined=__aeabi_ldivmod','--undefined=r1_time_state',str(objects[1]),'-o',str(registry)],check=True)
 small=out/'daily-metadata-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(registry),'-o',str(small)],check=True);su,sd=undefined_symbols(small);assert su==['nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get']
 linked=out/'native-daily-metadata-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert not any(x in u for x in ['r1_native_activity_cache_initialize','r1_native_hr_cache_initialize','r1_native_hrv_cache_initialize','r1_native_spo2_cache_initialize','r1_native_stress_cache_initialize','r1_native_temperature_cache_initialize'])
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},time_provider_object_sha256=sha(registry),metadata_object_sha256=sha(small),metadata_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,whole_startup_graph_executed=False,physical_adc_verified=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Daily metadata source bundle three logging seams;',len(u),'startup imports remain')
if __name__=='__main__':main()
