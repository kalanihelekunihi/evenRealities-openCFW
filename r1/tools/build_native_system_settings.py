#!/usr/bin/env python3
"""Compile build-only native native system settings and KV bit helpers."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'native-system-settings';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
 source=ROOT/'r1/components/runtime/native_system_settings.c';obj=out/'native_system_settings.o';dep=out/'native_system_settings.d'
 cmd=['clang','--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-munaligned-access','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fshort-enums','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-fno-delete-null-pointer-checks','-I'+str(ROOT/'r1/reconstructed'),'-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),'-DNRF52840_XXAA','-I'+str(ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/components/softdevice/s140/headers'),'-I'+str(ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/modules/nrfx/mdk'),'-I'+str(ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/components/toolchain/cmsis/include'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
 undefined,defined=undefined_symbols(obj);row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
 inputs={str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p:sha(Path(p)) for p in dep.read_text().replace('\\\n',' ').split(':',1)[1].split()}
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,h in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==h,p
 (out/'report.json').write_text(json.dumps(dict(units=[row],inputs=inputs,sdk_archive_sha256=sha(archive),sdk_svc_id=63,application_linked=False,instruction_identity=False),indent=2)+'\n');print('Native system settings and KV bit helpers compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()
