#!/usr/bin/env python3
"""Build native FlashDB sector reader and expose partition-read dependency."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-flashdb-sector-read';parent=BASE/'native-flashdb-log-read';pr=parent/'report.json';p=json.loads(pr.read_text());inputs=dict(p['inputs'])
 for path,h in inputs.items():assert sha(ROOT/path)==h,path
 src=ROOT/'r1/components/runtime/native_flashdb_sector_read.c';obj=out/'native_flashdb_sector_read.o';cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-Os','-ffreestanding','-fshort-enums','-Wall','-Wextra','-Werror','-c',str(src),'-o',str(obj)];subprocess.run(cmd,check=True)
 for x in [src,Path(__file__)]:inputs[str(x.relative_to(ROOT))]=sha(x)
 po=parent/'native-flashdb-log-read-runtime.o';assert sha(po)==p['linked_sha256'];linked=out/'native-flashdb-sector-read-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',str(po),str(obj),'-o',str(linked)],check=True);u=undefined_symbols(linked)[0];closed=sorted(set(p['undefined_symbols'])-set(u));assert closed==['r1_fdb_native_read_sector']
 roots=['r1_fdb_native_read_sector','r1_health_sync_provider_00063ad8','r1_health_sync_provider_00063cb4'];graph=out/'sector-read-source.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*[v for n in roots for v in ['-u',n]],str(linked),'-o',str(graph)],check=True)
 report=dict(units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined_symbols(obj)[0])],inputs=inputs,parent_report_sha256=sha(pr),parent_object_sha256=sha(po),linked_sha256=sha(linked),graph_object_sha256=sha(graph),undefined_symbols=u,graph_undefined_symbols=undefined_symbols(graph)[0],roots=roots,closed_parent_imports=closed,newly_exposed_imports=sorted(set(u)-set(p['undefined_symbols'])),native_body_bytes=360,instruction_identity_at_native_verification_placements=True,whole_image_complete=False,hardware_write_executed=False)
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('FlashDB sector reader: one import closed; '+str(len(u))+' unresolved imports')
if __name__=='__main__':main()
