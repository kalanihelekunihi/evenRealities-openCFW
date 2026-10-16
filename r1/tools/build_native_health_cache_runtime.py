#!/usr/bin/env python3
"""Consolidate cache payloads around existing metadata without duplicate state."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
LAYOUT=ROOT/'r1/source-config/runtime/native_health_cache.ld'
def symbols(obj):
 return {v[3]:(int(v[0],16),int(v[1],16),v[2]) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(obj)],text=True).splitlines() if len(v:=line.split())==4}
def main():
 out=BASE/'native-health-cache-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(LAYOUT.relative_to(ROOT)):sha(LAYOUT)}
 for directory,name,key in [('native-hourly-snapshot-runtime','native-hourly-snapshot-runtime.o','linked_sha256'),('native-health-cache','native_health_cache.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-health-cache-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','-T',str(LAYOUT),*map(str,objects),'-o',str(linked)],check=True)
 u,d=undefined_symbols(linked);old=undefined_symbols(objects[0])[0];closed=['r1_activity_daily_cache_accessor','r1_hr_daily_cache_accessor','r1_hrv_daily_cache_accessor','r1_spo2_daily_cache_accessor'];assert sorted(set(old)-set(u))==closed and not(set(u)-set(old)) and len(u)==24
 s=symbols(linked);sections=allocated_sections(linked);locations={}
 for name,size,offset,ts in [('activity',584,576,580),('hr',84,72,80),('spo2',84,72,80),('hrv',160,144,156)]:
  base=s['r1_cache_'+name][0];assert s['r1_daily_'+name+'_offset'][0]==base+offset and s['r1_daily_'+name+'_timestamp'][0]==base+ts
  section='.r1.health.cache.'+name;assert sections[section][2]==size and sections[section][4]==hashlib.sha256(bytes(size)).hexdigest();locations[name]=dict(bytes=size,offset_at=offset,timestamp_at=ts,section=section)
  assert '.r1.daily.'+name+'.offset' not in sections and '.r1.daily.'+name+'.timestamp' not in sections
 roots=closed+['r1_activity_daily_cache_reset','r1_heart_rate_daily_cache_reset','r1_spo2_daily_cache_reset','r1_hrv_daily_cache_reset'];graph=out/'health-cache-source.o'
 subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[arg for root in roots for arg in ['-u',root]],str(linked),'-o',str(graph)],check=True);assert undefined_symbols(graph)[0]==[]
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),graph_object_sha256=sha(graph),graph_roots=roots,undefined_symbols=u,closed_parent_imports=closed,newly_exposed_imports=[],cache_layout=locations,new_source_zero_bytes=888,existing_metadata_bytes_reused=24,consolidated_cache_bytes=912,canonical_metadata_reused=True,composed_runtime_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Health caches share existing metadata:24 imports;888 new source-zero bytes')
if __name__=='__main__':main()
