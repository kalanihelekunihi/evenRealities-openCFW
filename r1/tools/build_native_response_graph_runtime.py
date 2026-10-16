#!/usr/bin/env python3
"""Compose registered response/header/phone bodies with actual encoder and send hook."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-response-graph-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for name in ['native-protocol-response','native-protocol-response-header','native-phone-operation','native-protocol-connection-gates','native-nordic-delay-runtime']:
  rp=BASE/name/'report.json';r=json.loads(rp.read_text());obj=rp.parent/('native-nordic-delay-runtime.o' if name=='native-nordic-delay-runtime' else Path(r['units'][0]['source']).stem+'.o');assert sha(obj)==(r['linked_sha256'] if name=='native-nordic-delay-runtime' else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 variants=[];units=[]
 for name in ['native_protocol_encoder_body','native_protocol_send_hook_body']:
  source=ROOT/('r1/components/runtime/'+name+'.c');obj=out/(name+'.o');dep=out/(name+'.d');cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-munaligned-access','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-fno-delete-null-pointer-checks','-I'+str(ROOT/'r1/components/board'),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);variants.append(obj);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),defined=undefined_symbols(obj)[1],undefined=undefined_symbols(obj)[0]))
  for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(p);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
 erp=BASE/'native-protocol-encoder/report.json';er=json.loads(erp.read_text());eo=erp.parent/'native_protocol_encoder.o';assert sha(eo)==er['units'][0]['object_sha256'];reports[str(erp.relative_to(BASE))]=sha(erp)
 for p,h in er['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 mapobj=out/'version-map-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_protocol_version_map',str(eo),'-o',str(mapobj)],check=True);variants.append(mapobj)
 roots=['r1_protocol_sequence','r1_protocol_version_map','r1_protocol_send_hook','r1_stock_crc16_modbus','memmove','r1_phone_connection_handle_get','r1_connection_field10'];helpers=out/'response-helpers-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(objects[-1]),'-o',str(helpers)],check=True)
 small=out/'response-graph-source.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects[:-1]),*map(str,variants),str(helpers),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-response-graph-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),*map(str,variants),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[-1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_protocol_send_response','r1_protocol_response_send_0x100','r1_phone_cmd_send_op1'} and not new
 r=dict(units=units,inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects+variants},helpers_object_sha256=sha(helpers),graph_object_sha256=sha(small),graph_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),whole_allocator_ble_or_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Response graph runtime:',len(u),'imports;graph fixtures',su)
if __name__=='__main__':main()
