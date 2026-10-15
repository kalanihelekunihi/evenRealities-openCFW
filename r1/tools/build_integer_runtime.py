#!/usr/bin/env python3
"""Compile pinned LLVM unsigned division and recovered R1 integer EABI contracts."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    vendor=ROOT/'third-party/upstream/llvm-compiler-rt-format-20.1.8';pinfile=ROOT/'r1/source-config/runtime/llvm_integer_provenance.json';pin=json.loads(pinfile.read_text());assert pin['commit']=='87f0227cb60147a26a1eeb4fb06e3b505e9c7261'
    for row in pin['files']:assert sha(ROOT/row['path'])==row['sha256']
    out=BASE/'integer-runtime';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(ROOT/'r1/source-config/runtime'),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include')]
    rows=[];objects=[];inputs={str(pinfile.relative_to(ROOT)):sha(pinfile),**{r['path']:r['sha256'] for r in pin['files']}}
    for source in [vendor/'udivmoddi4.c',ROOT/'r1/components/runtime/integer_eabi.c']:
        obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');cmd=['clang',*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
        for path in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():inputs[str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else path]=sha(Path(path))
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    linked=out/'integer-runtime.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);remaining,_=undefined_symbols(linked);assert not remaining,remaining
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,upstream=pin,license_sha256=sha(ROOT/'r1/source-config/runtime/LLVM-COMPILER-RT-LICENSE.TXT'),relocatable_sha256=sha(linked),remaining_symbols=remaining,instruction_identity_proven=False,original_runtime_source_proven=False),indent=2)+'\n');print('Two integer C units compiled; four EABI entries; no unresolved symbols')
if __name__=='__main__':main()
