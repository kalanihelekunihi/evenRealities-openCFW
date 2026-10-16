#!/usr/bin/env python3
"""Reuse the source reset workspace and existing RTOS/delayed providers for ACK handling."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-protocol-ack-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-protocol-ack','native_protocol_ack.o',None),('native-health-commands-runtime','native-health-commands-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 workspace=out/'workspace-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_protocol_reset_workspace',str(objects[1]),'-o',str(workspace)],check=True);assert not undefined_symbols(workspace)[0]
 small=out/'protocol-ack-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(workspace),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-protocol-ack-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((BASE/'native-health-commands-runtime/report.json').read_text())['undefined_symbols']);assert old-set(u)=={'r1_packet_ack_handler','r1_delayed_event_restart'} and not set(u)-old
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},workspace_object_sha256=sha(workspace),ack_object_sha256=sha(small),ack_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,whole_ack_rtos_graph_executed=False,whole_startup_graph_executed=False,physical_concurrency_verified=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('ACK source runtime:',len(u),'imports;packet ACK and delayed restart resolved')
if __name__=='__main__':main()
