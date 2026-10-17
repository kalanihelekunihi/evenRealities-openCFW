#!/usr/bin/env python3
"""Compile multicast body without inventing unresolved configuration owners."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';OUT=BASE/'native-record-update';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parent=BASE/'native-charge-notification';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_record_update.c';obj=OUT/'native_record_update.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for f in [src,Path(__file__)]:inputs[str(f.relative_to(ROOT))]=sha(f)
 libc=BASE/'native-libc-sequences';lr=json.loads((libc/'report.json').read_text());lo=libc/'native_libc_sequences.o';assert sha(lo)==lr['units'][0]['object_sha256']
 for path,h in lr['inputs'].items():assert sha(ROOT/path)==h;inputs[path]=h
 selected=OUT/'memcmp-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_native_memcmp',str(lo),'-o',str(selected)],check=True);inputs[str(lo.relative_to(ROOT))]=sha(lo)
 po=parent/'native-charge-notification-runtime.o';assert sha(po)==p['linked_sha256'];linked=OUT/'native-record-update-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),str(selected),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));added=sorted(set(u)-set(p['undefined_symbols']));assert closed==['r1_event_service_0006c66c'] and added==['r1_record12_apply','r1_record12_persist'] and len(u)==66
 roots=p['roots']+closed;graph=OUT/'report-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 b=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=closed,newly_exposed_imports=added,native_body_bytes=102,native_source_span_bytes=104,new_ram_state_bytes=0,whole_image_complete=False,hardware_write_executed=False)
 (OUT/'report.json').write_text(json.dumps(b,indent=2)+'\n');print('Record update compiles;one import closes;two providers exposed;66 remain')
if __name__=='__main__':main()
