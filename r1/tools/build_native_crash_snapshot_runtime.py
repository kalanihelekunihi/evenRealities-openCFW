#!/usr/bin/env python3
"""Compose snapshot; preserve health-cache provider boundaries."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-crash-snapshot-runtime';out.mkdir(exist_ok=True);objects=[];reports={};inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}
 for directory,name,key in [('native-crash-initialize-runtime','native-crash-initialize-runtime.o','linked_sha256'),('native-crash-snapshot','native_crash_snapshot.o',None)]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 linked=out/'native-crash-snapshot-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True)
 u,d=undefined_symbols(linked);old=undefined_symbols(objects[0])[0];assert sorted(set(old)-set(u))==['r1_health_crash_snapshot_builder'] and sorted(set(u)-set(old))==['r1_activity_daily_cache_accessor','r1_hr_daily_cache_accessor','r1_hr_hour_query','r1_hrv_daily_cache_accessor','r1_spo2_daily_cache_accessor'] and len(u)==29
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=['r1_health_crash_snapshot_builder'],newly_exposed_imports=['r1_activity_daily_cache_accessor','r1_hr_daily_cache_accessor','r1_hr_hour_query','r1_hrv_daily_cache_accessor','r1_spo2_daily_cache_accessor'],canonical_reset_context_reused=True,composed_runtime_execution_verified=False,instruction_identity=False,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Crash snapshot linked; five health providers exposed:29 imports')
if __name__=='__main__':main()
