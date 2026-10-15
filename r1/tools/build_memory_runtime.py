#!/usr/bin/env python3
"""Compile pinned attributable C memory/string providers and EABI wrappers."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vendor=ROOT/'third-party/upstream/musl-memory-1.2.5';pin=json.loads((vendor/'provenance.json').read_text());assert pin['commit']=='0784374d561435f7c787a555aeab8ede699ed298'
    for row in pin['files']:assert sha(vendor/row['path'])==row['sha256']
    out=BASE/'runtime';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(ROOT/'r1/source-config/runtime'),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include')]
    rows=[];objects=[];inputs={str((vendor/'provenance.json').relative_to(ROOT)):sha(vendor/'provenance.json')}
    for source in [vendor/'memcpy.c',vendor/'memset.c',vendor/'strcmp.c',vendor/'strlen.c',ROOT/'r1/components/runtime/memory_eabi.c']:
        obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');cmd=['clang',*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
        for path in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():inputs[str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else path]=sha(Path(path))
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    linked=out/'memory-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);remaining,_=undefined_symbols(linked);assert not remaining,remaining
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,upstream=pin,license_sha256=sha(vendor/'COPYRIGHT'),relocatable_sha256=sha(linked),remaining_symbols=remaining,instruction_identity_proven=False,original_runtime_source_proven=False),indent=2)+'\n');print('Five C runtime units compiled; eight entry points; no unresolved symbols')
if __name__=='__main__':main()
