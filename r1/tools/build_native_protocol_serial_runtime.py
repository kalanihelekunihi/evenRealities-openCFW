#!/usr/bin/env python3
"""Use existing attributable movement/fill and shared KV/response providers for serial reporting."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-protocol-serial-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-protocol-serial','native_protocol_serial.o',None),('native-protocol-ack-runtime','native-protocol-ack-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 memory=out/'serial-memory-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_native_memory_move','--undefined=memset',str(objects[1]),'-o',str(memory)],check=True);assert not undefined_symbols(memory)[0]
 small=out/'protocol-serial-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(memory),'-o',str(small)],check=True);su,sd=undefined_symbols(small);assert su==['r1_kv_class_read','r1_protocol_send_response']
 linked=out/'native-protocol-serial-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((BASE/'native-protocol-ack-runtime/report.json').read_text())['undefined_symbols']);assert old-set(u)=={'r1_device_serial_handler','r1_device_info_kv_handle'} and not set(u)-old
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},memory_object_sha256=sha(memory),serial_object_sha256=sha(small),serial_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,whole_kv_transport_graph_executed=False,whole_startup_graph_executed=False,physical_serial_or_delivery_verified=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Serial runtime:',len(u),'imports;serial handler and shared124-byte KV handle now resolved')
if __name__=='__main__':main()
