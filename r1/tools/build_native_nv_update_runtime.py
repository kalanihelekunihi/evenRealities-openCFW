#!/usr/bin/env python3
"""Join NV update bodies and canonical seven-handle source table."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-nv-update-runtime';out.mkdir(exist_ok=True);source=ROOT/'r1/components/runtime/native_nv_table_config.c';cfg=out/'native_nv_table_config.o';dep=out/'native_nv_table_config.d';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-fshort-enums','-std=c11','-Os','-ffreestanding','-fno-builtin','-fdata-sections','-Wall','-Wextra','-Werror','-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(cfg)];subprocess.run(cmd,check=True)
 layout=ROOT/'r1/source-config/runtime/native_nv_handle_composition.ld';inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__)),str(layout.relative_to(ROOT)):sha(layout)};reports={};objects=[]
 for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(p);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
 for name,filename,key in [('native-nv-update','native_nv_update.o',None),('native-system-event-runtime','native-system-event-runtime.o','linked_sha256')]:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());obj=rp.parent/filename;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=out/'nv-cached-owners-source.o';roots=['r1_kv_class_read','r1_kv_class_write','memset','r1_device_info_record_kv_handle','r1_batcfg_record_kv_handle','r1_device_info_kv_handle'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(objects[1]),'-o',str(helpers)],check=True)
 extra=[]
 for name,filename,root in [('native-health-commands','native_health_commands.o','r1_protocol_send_flag_set_c'),('native-protocol-ack','native_protocol_ack.o','r1_packet_field12_get')]:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());obj=rp.parent/filename;assert sha(obj)==r['units'][0]['object_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
  p=out/(root+'.o');subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined='+root,str(obj),'-o',str(p)],check=True);extra.append(p)
 small=out/'nv-update-source.o';subprocess.run(['arm-none-eabi-ld','-r','-T',str(layout),str(cfg),str(objects[0]),str(helpers),*map(str,extra),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-nv-update-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','-T',str(layout),str(cfg),*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_protocol_command_000844b0','r1_health_record_kv_handle'} and new=={'r1_store_class_record_write'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},config_object_sha256=sha(cfg),cached_owners_sha256=sha(helpers),helpers={p.name:sha(p) for p in extra},graph_object_sha256=sha(small),graph_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),canonical_seven_handle_table=True,whole_flash_commit_or_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('NV update runtime:',len(u),'imports;graph fixtures:',su)
if __name__=='__main__':main()
