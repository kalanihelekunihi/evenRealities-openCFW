#!/usr/bin/env python3
"""Compose actual source memory helper and BLE message encoding."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-ble-message-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-ble-message','native_ble_message.o',None),('native-protocol-control-runtime','native-protocol-control-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=out/'message-helpers-source.o';roots=['r1_native_memory_move','r1_protocol_service_thread'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(objects[1]),'-o',str(helpers)],check=True)
 small=out/'ble-message-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(helpers),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-ble-message-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((BASE/'native-protocol-control-runtime/report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_ble_thread_message_encode'} and not new
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},helper_object_sha256=sha(helpers),message_object_sha256=sha(small),message_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),whole_dispatch_or_rtos_graph_executed=False,whole_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('BLE message runtime:',len(u),'imports;',len(closed),'closed;',len(new),'new provider seams;unit imports',su)
if __name__=='__main__':main()
