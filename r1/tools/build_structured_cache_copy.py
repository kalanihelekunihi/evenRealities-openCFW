#!/usr/bin/env python3
"""Compile native structured logger over authenticated CMSIS intrinsics."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'structured-cache-copy';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 source=ROOT/'r1/components/board/structured_cache_copy.c';obj=out/'structured_cache_copy.o';dep=out/'structured_cache_copy.d';sdk=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560'
 cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(sdk/'components/toolchain/cmsis/include'),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 inputs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p:sha(Path(p)) for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split()}
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for path,digest in inputs.items():
   if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
 undefined,defined=undefined_symbols(obj);row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
 (out/'report.json').write_text(json.dumps(dict(units=[row],inputs=inputs,application_linked=False,instruction_identity_proven=False),indent=2)+'\n');print('Native cache-copy body compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()
