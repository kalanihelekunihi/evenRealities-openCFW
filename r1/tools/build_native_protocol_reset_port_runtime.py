#!/usr/bin/env python3
"""Compose source reset/port registration and link actual callback bodies into startup."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-protocol-reset-port-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects={}
 specs=[('native-protocol-reset-runtime','protocol-reset-source.o','reset_object_sha256'),('native-protocol-reset-runtime','native-protocol-reset-runtime.o','linked_sha256'),('native-protocol-port','native_protocol_port.o',None),('native-protocol-send-registration','native_protocol_send_registration.o',None),('native-protocol-send-hook','native_protocol_send_hook.o',None),('native-protocol-fragment','native_protocol_fragment.o',None),('native-protocol-fragment-state','native_protocol_fragment_state.o',None),('native-protocol-ingress','native_protocol_ingress.o',None)]
 for directory,name,key in specs:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects[name]=obj;reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 root_report=BASE/'native-reset-retained/report.json';cr=json.loads(root_report.read_text());unit=next(x for x in cr['units'] if x['source']=='r1/source/stock_checksums.c');checksums=Path(unit['command'][-1]);assert sha(checksums)==unit['object_sha256'];objects[checksums.name]=checksums;reports['native-reset-retained/report.json']=sha(root_report)
 for p,h in cr['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 selected=[]
 for name,symbol,obj in [('send-hook-cell.o','r1_protocol_send_hook',objects['native_protocol_send_hook.o']),('crc32-source.o','r1_stock_crc32_update',checksums)]:
  dest=out/name;subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined='+symbol,str(obj),'-o',str(dest)],check=True);assert not undefined_symbols(dest)[0];selected.append(dest)
 small=out/'protocol-reset-port-source.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(objects[name]) for name in ['protocol-reset-source.o','native_protocol_port.o','native_protocol_send_registration.o']],str(selected[0]),'-o',str(small)],check=True);su,sd=undefined_symbols(small);assert su==['nrf_log_frontend_std_0','r1_eus_ingress_plan_decode','r1_event_publish','r1_fragment_message','r1_native_delayed_schedule','r1_structured_log_format','r1_structured_log_mode_get']
 linked=out/'native-protocol-reset-port-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(objects[name]) for name in ['native-protocol-reset-runtime.o','native_protocol_port.o','native_protocol_send_registration.o','native_protocol_fragment.o','native_protocol_fragment_state.o','native_protocol_ingress.o']],*[str(p) for p in selected],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert not set(['r1_proto_port_init','r1_fragment_message','r1_eus_ingress_plan_decode','r1_protocol_send_callback_set'])&set(u)
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects.values()},selected_objects={p.name:sha(p) for p in selected},graph_object_sha256=sha(small),graph_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,callback_source_linked=True,callback_graph_executed=False,whole_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Source reset/port graph7 seams;',len(u),'startup imports with actual ingress/fragment bodies')
if __name__=='__main__':main()
