#!/usr/bin/env python3
"""Replace calendar frames and expose existing fallback/month-table owners."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();REPLACE=['r1_time_utc_offset_get','time_calendar_utc_to_calendar','time_calendar_unix_to_broken_down'];EXPOSE=['unix_to_broken_down_fallback','month_days_forward']
def main():
 out=BASE/'native-calendar-frames';parent=BASE/'native-health-average';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_calendar_frames.c';obj=out/'native_calendar_frames.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for x in [src,Path(__file__)]:inputs[str(x.relative_to(ROOT))]=sha(x)
 po=parent/'native-health-average-runtime.o';assert sha(po)==p['linked_sha256'];clone=out/'parent-calendar-symbols.o';subprocess.run(['arm-none-eabi-objcopy',*[v for n in REPLACE for v in ['--weaken-symbol',n]],*[v for n in EXPOSE for v in ['--globalize-symbol',n]],str(po),str(clone)],check=True);assert allocated_sections(po)==allocated_sections(clone)
 def nm(path):return Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(path)],text=True).splitlines())
 old=nm(po);new=nm(clone)
 for n,size,oldtype,newtype in [(n,s,'T','W') for n,s in zip(REPLACE,[14,132,388])]+[(EXPOSE[0],36,'b','B'),(EXPOSE[1],24,'r','R')]:
  row=('00000000','%08x'%size,oldtype,n);assert old[row]==1 and new[(row[0],row[1],newtype,n)]==1;del old[row];del new[(row[0],row[1],newtype,n)]
 assert old==new
 config=out/'shared-calendar-config.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in ['r1_time_state',*EXPOSE] for v in ['-u',n]],str(clone),'-o',str(config)],check=True);assert sum(x[2] for x in allocated_sections(config).values())==92
 linked=out/'native-calendar-frames-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(clone),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];assert u==p['undefined_symbols'] and len(u)==82
 roots=p['roots']+REPLACE;graph=out/'calendar-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 report=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),parent_symbol_clone_sha256=sha(clone),replacement_symbols=REPLACE,exposed_existing_config_symbols=EXPOSE,parent_allocated_sections_unchanged=True,parent_other_symbols_unchanged=True,shared_config_object_sha256=sha(config),shared_existing_config_bytes=92,new_ram_state_bytes=0,linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=[],newly_exposed_imports=[],native_body_bytes=310,native_source_span_bytes=328,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Three calendar frames linked;82 imports unchanged;92 existing configuration bytes reused')
if __name__=='__main__':main()
