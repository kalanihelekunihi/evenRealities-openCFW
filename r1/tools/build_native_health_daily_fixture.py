#!/usr/bin/env python3
"""Compile multicast body without inventing unresolved configuration owners."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-health-daily-fixture';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parent=BASE/'native-subscriber-consume';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_health_daily_fixture.c';obj=OUT/'native_health_daily_fixture.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for f in [src,Path(__file__)]:inputs[str(f.relative_to(ROOT))]=sha(f)
 rand_report=BASE/'native-libc-primitives/report.json';rand=json.loads(rand_report.read_text());rand_obj=BASE/'native-libc-primitives/native_libc_primitives.o';assert sha(rand_obj)==rand['units'][0]['object_sha256'];inputs.update(rand['inputs']);selected_rand=OUT/'selected-rand.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_native_rand',str(rand_obj),'-o',str(selected_rand)],check=True)
 po=parent/'native-subscriber-consume-runtime.o';assert sha(po)==p['linked_sha256'];linked=OUT/'native-health-daily-fixture-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),str(selected_rand),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));added=sorted(set(u)-set(p['undefined_symbols']));assert closed==['r1_event_service_0008b378'] and added==['r1_health_fixture_notify_hr','r1_health_fixture_notify_spo2','r1_health_fixture_notify_temperature'] and len(u)==79
 roots=p['roots']+closed+['r1_temperature_daily_cache_accessor'];graph=OUT/'fixture-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 b=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=closed,newly_exposed_imports=added,native_body_bytes=786,native_source_span_bytes=1192,new_ram_state_bytes=0,reused_rand_object_sha256=sha(selected_rand),reused_rand_report_sha256=sha(rand_report),whole_image_complete=False,hardware_write_executed=False)
 (OUT/'report.json').write_text(json.dumps(b,indent=2)+'\n');print('Daily fixture core/accessor compiled;one closes/three exposed;79 imports')
if __name__=='__main__':main()
