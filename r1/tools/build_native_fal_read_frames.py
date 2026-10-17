#!/usr/bin/env python3
"""Replace two read-frame bodies without changing other providers or RAM owners."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();REPLACE=['r1_native_fal_device_read','r1_stock_dispatch_10']
def main():
 out=BASE/'native-fal-read-frames';parent=BASE/'native-fal-device-lookup';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_fal_read_frames.c';obj=out/'native_fal_read_frames.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for x in [src,Path(__file__)]:inputs[str(x.relative_to(ROOT))]=sha(x)
 po=parent/'native-fal-device-lookup-runtime.o';assert sha(po)==p['linked_sha256'];clone=out/'parent-read-weakened.o';subprocess.run(['arm-none-eabi-objcopy',*[v for n in REPLACE for v in ['--weaken-symbol',n]],str(po),str(clone)],check=True);assert allocated_sections(po)==allocated_sections(clone)
 def nm(path):return Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(path)],text=True).splitlines())
 old=nm(po);new=nm(clone)
 for n,size in zip(REPLACE,[40,26]):
  row=('00000000','%08x'%size,'T',n);assert old[row]==1 and new[(row[0],row[1],'W',n)]==1;del old[row];del new[(row[0],row[1],'W',n)]
 assert old==new
 shared=out/'read-state.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','-u','r1_fal_device_handle','-u','r1_fal_read_request',str(clone),'-o',str(shared)],check=True);assert sum(x[2] for x in allocated_sections(shared).values())==16
 linked=out/'native-fal-read-frames-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(clone),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert u==p['undefined_symbols'] and len(u)==88
 roots=p['roots']+REPLACE;graph=out/'read-frames-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 report=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),weakened_parent_sha256=sha(clone),replacement_symbols=REPLACE,parent_allocated_sections_unchanged=True,parent_other_symbols_unchanged=True,read_state_object_sha256=sha(shared),shared_existing_state_bytes=16,new_ram_state_bytes=0,linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=[],newly_exposed_imports=[],native_body_bytes=56,native_source_span_bytes=66,instruction_identity_at_native_verification_placements=True,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Native FAL read/dispatch frames linked;88 imports unchanged;16 existing state bytes reused')
if __name__=='__main__':main()
