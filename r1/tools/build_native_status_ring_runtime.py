#!/usr/bin/env python3
"""Compose source-owned status ring and existing connection fields."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-status-ring-runtime';out.mkdir(exist_ok=True);inputs={str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))};reports={};objects=[]
 for directory,name,key in [('native-status-ring','native_status_ring.o',None),('native-phone-role-runtime','native-phone-role-runtime.o','linked_sha256')]:
  rp=BASE/directory/'report.json';r=json.loads(rp.read_text());obj=rp.parent/name;assert sha(obj)==(r[key] if key else r['units'][0]['object_sha256']);objects.append(obj);reports[str(rp.relative_to(BASE))]=sha(rp)
  for p,h in r['inputs'].items():assert sha(ROOT/p)==h,p;inputs[p]=h
 helpers=out/'status-fields-source.o';roots=['r1_connection_field8','r1_connection_field10'];subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(objects[1]),'-o',str(helpers)],check=True)
 small=out/'status-ring-source.o';subprocess.run(['arm-none-eabi-ld','-r',str(objects[0]),str(helpers),'-o',str(small)],check=True);su,sd=undefined_symbols(small)
 linked=out/'native-status-ring-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*[str(p) for p in objects],'-o',str(linked)],check=True);u,d=undefined_symbols(linked);old=set(json.loads((BASE/'native-phone-role-runtime/report.json').read_text())['undefined_symbols']);closed=old-set(u);new=set(u)-old;assert closed=={'r1_status_record_ring_publish','r1_charge_state_byte_get'} and new=={'r1_battery_runtime_update_service'}
 r=dict(inputs=inputs,provider_reports=reports,objects={str(p.relative_to(BASE)):sha(p) for p in objects},helper_object_sha256=sha(helpers),status_object_sha256=sha(small),status_undefined_symbols=su,linked_sha256=sha(linked),undefined_symbols=u,closed_parent_imports=sorted(closed),newly_exposed_imports=sorted(new),whole_dispatch_or_rtos_graph_executed=False,whole_startup_graph_executed=False,instruction_identity=False,whole_image_complete=False)
 (out/'report.json').write_text(json.dumps(r,indent=2)+'\n');print('Status-ring runtime:',len(u),'imports;',len(closed),'closed;',len(new),'new provider seams;unit imports',su)
if __name__=='__main__':main()
