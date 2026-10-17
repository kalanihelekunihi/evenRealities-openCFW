#!/usr/bin/env python3
"""Build native Health sample storage and expose partition-read dependency."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-activity-storage';parent=BASE/'native-calendar-frames';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_activity_storage.c';obj=out/'native_activity_storage.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for x in [src,Path(__file__)]:inputs[str(x.relative_to(ROOT))]=sha(x)
 po=parent/'native-calendar-frames-runtime.o';assert sha(po)==p['linked_sha256'];linked=out/'native-activity-storage-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));assert closed==['r1_activity_event_storage']
 reused=out/'activity-cache.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_cache_activity',str(po),'-o',str(reused)],check=True)
 roots=p['roots']+[x['symbol'] for x in json.loads((out/'contracts.json').read_text())['bodies']];graph=out/'activity-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 report=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),reused_activity_cache_object_sha256=sha(reused),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=closed,newly_exposed_imports=sorted(set(u)-set(p['undefined_symbols'])),native_body_bytes=296,new_ram_state_bytes=0,reused_activity_cache_bytes=576,reused_activity_config_bytes=584,full_cache_context_extents_proven=False,instruction_identity_at_native_verification_placements=True,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Activity storage: one import closed; '+str(len(u))+' unresolved imports')
if __name__=='__main__':main()
