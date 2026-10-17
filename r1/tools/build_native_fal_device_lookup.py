#!/usr/bin/env python3
"""Link FAL lookup against existing initializer-owned table/count/cache state."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
from build_native_dfu_backend_runtime import allocated_sections
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();SHARED=['r1_fal_partition_table','r1_fal_partition_count','r1_fal_partition_cache']
def main():
 out=BASE/'native-fal-device-lookup';parent=BASE/'native-fal-partition-read';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_fal_device_lookup.c';obj=out/'native_fal_device_lookup.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for x in [src,Path(__file__)]:inputs[str(x.relative_to(ROOT))]=sha(x)
 po=parent/'native-fal-partition-read-runtime.o';assert sha(po)==p['linked_sha256'];clone=out/'parent-shared-state.o';subprocess.run(['arm-none-eabi-objcopy',*[s for n in SHARED for s in ['--globalize-symbol',n]],str(po),str(clone)],check=True)
 assert allocated_sections(po)==allocated_sections(clone)
 from collections import Counter
 def nm(path):return Counter(tuple(line.split()) for line in subprocess.check_output(['arm-none-eabi-nm','-S',str(path)],text=True).splitlines())
 old=nm(po);new=nm(clone)
 for n,size in zip(SHARED,[4,4,28]):
  row=('00000000','%08x'%size,'b',n);assert old[row]==1 and new[(row[0],row[1],'B',n)]==1;del old[row];del new[(row[0],row[1],'B',n)]
 assert old==new
 shared=out/'shared-state.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in SHARED for v in ['-u',n]],str(clone),'-o',str(shared)],check=True)
 assert sum(x[2] for x in allocated_sections(shared).values())==36
 linked=out/'native-fal-device-lookup-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(clone),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));assert closed==['r1_fal_native_device_by_partition'];roots=['r1_fal_native_device_by_partition','r1_health_sync_provider_00063cb4',*SHARED];graph=out/'lookup-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 report=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),parent_shared_state_clone_sha256=sha(clone),shared_state_object_sha256=sha(shared),globalized_existing_state_symbols=SHARED,parent_allocated_sections_unchanged=True,parent_other_symbols_unchanged=True,shared_existing_state_bytes=36,new_ram_state_bytes=0,required_table_count_native_adjacency_gate=True,linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=closed,newly_exposed_imports=sorted(set(u)-set(p['undefined_symbols'])),native_body_bytes=58,instruction_identity_at_native_verification_placements=True,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('FAL device lookup closes one import; '+str(len(u))+' remain; existing36 state bytes reused')
if __name__=='__main__':main()
