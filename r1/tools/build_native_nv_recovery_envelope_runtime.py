#!/usr/bin/env python3
"""Build native envelope alias without supplying persistent recovery dispatch."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-nv-recovery-envelope-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-nv-recovery-envelope','native_nv_recovery_envelope.o',None),('native-nv-class-writer-runtime','native-nv-class-writer-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 owner=out/'envelope-existing-helpers-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_packet_field12_get','--undefined=r1_phone_connection_handle_get',str(objects[1]),'-o',str(owner)],check=True)
 rp=BASE/'native-protocol-serial/report.json';r=json.loads(rp.read_text());serial=rp.parent/'native_protocol_serial.o';assert sha(serial)==r['units'][0]['object_sha256'];reports[str(rp.relative_to(BASE))]=sha(rp)
 for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 header=out/'inverse-header-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_protocol_send_flag_inv',str(serial),'-o',str(header)],check=True)
 small=out/'nv-recovery-envelope-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(owner),str(header),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-nv-recovery-envelope-runtime.o';subprocess.run(['arm-none-eabi-ld','-r','--defsym=r1_nv_recovery_command_handler_plan_decode=r1_native_nv_recovery_envelope_handler',*map(str,objects),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((objects[1].parent/'report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_nv_recovery_command_handler_plan_decode'} and new=={'r1_native_nv_recovery_command_dispatch'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},owner_object_sha256=sha(owner),header_object_sha256=sha(header),envelope_object_sha256=sha(small),envelope_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),native_envelope_alias=['r1_nv_recovery_command_handler_plan_decode','r1_native_nv_recovery_envelope_handler'],bounded_planner_modified=False,persistent_dispatch_supplied=False,hardware_write_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Build-only recovery envelope:',len(u),'imports;lower native dispatch remains unresolved;unit fixtures',su)
if __name__=='__main__':main()
