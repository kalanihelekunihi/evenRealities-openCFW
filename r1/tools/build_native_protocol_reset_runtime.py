#!/usr/bin/env python3
"""Link reset bodies with existing sequence cell and attributable source clear."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-protocol-reset-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name in [('native-protocol-reset','native_protocol_reset.o'),('native-daily-metadata-runtime','native-daily-metadata-runtime.o'),('native-protocol-encoder','native_protocol_encoder.o')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r.get('linked_sha256') or r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 selected=[]
 for name,symbol,obj in [('clear-source.o','__aeabi_memclr',objects[1]),('sequence-source.o','r1_protocol_sequence',objects[2])]:
  dest=out/name;subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined='+symbol,str(obj),'-o',str(dest)],check=True);assert not undefined_symbols(dest)[0];selected.append(dest)
 small=out/'protocol-reset-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),*[str(p) for p in selected],'-o',str(small)],check=True);su,sd=undefined_symbols(small);assert su==['r1_event_publish','r1_native_delayed_schedule','r1_proto_port_init']
 linked=out/'native-protocol-reset-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(objects[1]),str(selected[1]),'-o',str(linked)],check=True);u,d=undefined_symbols(linked);assert 'r1_native_proto_port_reset' not in u and 'r1_proto_port_init' in u
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},selected_objects={p.name:sha(p) for p in selected},reset_object_sha256=sha(small),reset_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,whole_startup_graph_executed=False,whole_protocol_init_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Reset source3 provider seams;',len(u),'startup imports;port-init newly exposed')
if __name__=='__main__':main()
