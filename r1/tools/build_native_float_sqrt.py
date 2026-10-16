#!/usr/bin/env python3
"""Compile native native raw-bit integer square root."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-float-sqrt';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 source=ROOT/'r1/components/runtime/native_float_sqrt.c';obj=out/'native_float_sqrt.o';dep=out/'native_float_sqrt.d'
 cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-munaligned-access','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-fno-delete-null-pointer-checks','-I'+str(ROOT/'r1/reconstructed'),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 undefined,defined=undefined_symbols(obj);row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
 inputs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p:sha(Path(p)) for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split()}
 (out/'report.json').write_text(json.dumps(dict(units=[row],inputs=inputs,application_linked=False,instruction_identity=False),indent=2)+'\n');print('Native square-root helper compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()
