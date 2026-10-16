#!/usr/bin/env python3
"""Bind cold KV classes, existing YHM readiness and native timestamp source alias."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-battery-kv-runtime';out.mkdir(exist_ok=True);source=ROOT/'r1/components/runtime/native_battery_kv_config.c';cfg=out/'native_battery_kv_config.o';dep=out/'native_battery_kv_config.d';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-fshort-enums','-std=c11','-Os','-ffreestanding','-fno-builtin','-fdata-sections','-Wall','-Wextra','-Werror','-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(cfg)];subprocess.run(cmd,check=True)
 inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={}
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(p);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
 parent=BASE/'native-battery-context-runtime/native-battery-context-runtime.o';yp=BASE/'native-yhm-frontend/native_yhm_frontend.o'
 for name,obj,key in [('native-battery-context-runtime',parent,'linked_sha256'),('native-yhm-frontend',yp,None)]:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 ready=out/'yhm-readiness-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_yhm_ready_native',str(yp),'-o',str(ready)],check=True)
 helpers=out/'kv-cached-helpers-source.o';roots=['r1_batcfg_byte0_get','r1_batcfg_flag1_get','r1_batcfg_word1_signed_get','r1_kv_dev_info_fields_set','r1_kv_class_read','r1_kv_class_write'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(parent),'-o',str(helpers)],check=True)
 small=out/'battery-kv-cached-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(cfg),str(helpers),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-battery-kv-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','--defsym=time_backend_timestamp_thunk=r1_time_backend_timestamp',str(cfg),str(ready),str(parent),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((parent.parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_batcfg_record_kv_handle','r1_device_info_record_kv_handle','r1_yhm_ready_native','time_backend_timestamp_thunk'} and not new
 r=dict(inputs=inputs,provider_reports=reports,objects={str(parent.relative_to(BASE)):sha(parent),str(yp.relative_to(BASE)):sha(yp)},config_object_sha256=sha(cfg),readiness_object_sha256=sha(ready),helpers_object_sha256=sha(helpers),cached_object_sha256=sha(small),cached_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),timestamp_alias=['time_backend_timestamp_thunk','r1_time_backend_timestamp'],whole_kv_hardware_or_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Battery KV runtime:',len(u),'imports;',len(closed),'closed;',len(new),'new;cached imports',su)
if __name__=='__main__':main()
