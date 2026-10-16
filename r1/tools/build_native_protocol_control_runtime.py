#!/usr/bin/env python3
"""Compose existing payload/header/handle helpers with system control source."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-protocol-control-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-protocol-control','native_protocol_control.o',None),('native-protocol-serial-runtime','native-protocol-serial-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=out/'control-helpers-source.o';roots=['r1_packet_field12_get','r1_protocol_send_flag_set_c','r1_protocol_send_checked','r1_phone_connection_handle_get','r1_health_report_setting_plan'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(objects[1]),'-o',str(helpers)],check=True)
 small=out/'protocol-control-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(helpers),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-protocol-control-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((BASE/'native-protocol-serial-runtime/report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_connection_control_adv_start_handler_plan_decode','r1_pair_role_handler','r1_protocol_command_00083e2c','r1_service_health_report_set'} and new=={'r1_ble_thread_message_encode','r1_phone_connection_role_assign'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},helper_object_sha256=sha(helpers),control_object_sha256=sha(small),control_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),whole_dispatch_or_rtos_graph_executed=False,whole_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Control runtime:',len(u),'imports;',len(closed),'closed;',len(new),'new provider seams;unit imports',su)
if __name__=='__main__':main()
