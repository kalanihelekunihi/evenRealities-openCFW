#!/usr/bin/env python3
"""Select unchanged pinned FAL readiness core initializer and readiness without copying bodies."""
import hashlib,json,subprocess
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-fal-partition';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 tree=ROOT/'third-party/upstream/flashdb-2.0.0';pin='4e5677408256f82d47cd56a6b04605dcee35ed9a';assert subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()==pin;assert not subprocess.check_output(['git','-C',str(tree),'status','--porcelain'],text=True).strip()
 pr=BASE/'public-providers/report.json';row=next(r for r in json.loads(pr.read_text())['units'] if r['source'].endswith('/fal_partition.c'));flags=row['command'][1:row['command'].index('-c')];src=ROOT/row['source'];raw=out/'fal_partition.o';obj=out/'fal-partition.o';dep=out/'fal_partition.d'
 cmd=['clang','-I'+str(ROOT/'r1/components/board/fal-native'),*flags,'-fshort-enums','-ffunction-sections','-fdata-sections','-include',str(ROOT/'r1/components/board/fal-native/partition_configuration.h'),'-O0','-fno-inline','-Dinit_ok=r1_fal_partition_initialized','-Dpartition_table=r1_fal_partition_table','-Dpartition_table_len=r1_fal_partition_count','-Dpart_flash_cache=r1_fal_partition_cache','-Dpartition_table_def=r1_fal_partition_records','-MD','-MF',str(dep),'-c',str(src),'-o',str(raw)];subprocess.run(cmd,check=True)
 # Retain the original upstream symbol as well as the product-facing alias.
 link=['arm-none-eabi-ld','-r','--gc-sections','--undefined=fal_partition_init','--undefined=fal_partition_find',str(raw),'-o',str(obj)];subprocess.run(link,check=True)
 inputs={}
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 undefined,defined=undefined_symbols(obj);assert set(undefined)=={'fal_flash_device_find','strcmp','printf'}
 (out/'report.json').write_text(json.dumps(dict(upstream_pin=pin,upstream_source=str(src.relative_to(ROOT)),upstream_source_sha256=sha(src),inputs=inputs,public_report_sha256=sha(pr),units=[dict(source=str(src.relative_to(ROOT)),source_sha256=sha(src),command=link,compile_command=cmd,raw_object_sha256=sha(raw),compiled=True,object_sha256=sha(obj),defined=defined,undefined=undefined)],scope='Unchanged pinned FAL partition init/find/cache validation with native assertions/errors and authenticated seven-row table',limitations=['Device lookup and printf are explicit providers.','Driver callbacks and runtime printf remain external; hardware behavior remains unproven.'],instruction_identity_proven=False),indent=2)+'\n');print('Pinned FAL partition providers compiled')
if __name__=='__main__':main()
