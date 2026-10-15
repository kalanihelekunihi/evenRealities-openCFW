#!/usr/bin/env python3
"""Compile native watchdog manager/port/device/config using pinned CMSIS/Nordic APIs."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'watchdog-startup';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sdk_report=BASE/'application-sdk/report.json';app=json.loads(sdk_report.read_text());sdk=next(r for r in app['units'] if r['source'].endswith('/nrfx_wdt.c'));flags=sdk['command'][1:sdk['command'].index('-c')];rows=[];objects=[];inputs={}
 for name in ('native_watchdog_manager','native_watchdog_port','native_watchdog_device','native_named_wdt'):
  source=ROOT/('r1/components/board/'+name+'.c');obj=out/(name+'.o');dep=out/(name+'.d');cmd=['clang',*flags,'-fno-delete-null-pointer-checks','-I'+str(ROOT/'r1/reconstructed'),'-I'+str(ROOT/'r1/components/registry'),'-I'+str(ROOT/'third-party/upstream/cmsis-5-590/CMSIS/RTOS2/Include'),'-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True)
  for path in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():inputs[str(Path(path).relative_to(ROOT)) if Path(path).is_relative_to(ROOT) else path]=sha(Path(path))
  undefined,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for path,digest in inputs.items():
   if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
 sdk_object=Path(sdk['command'][-1]);assert sha(sdk_object)==sdk['object_sha256'] and sha(ROOT/sdk['source'])==sdk['source_sha256'];objects.append(sdk_object)
 linked=out/'native-watchdog-startup.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);remaining,_=undefined_symbols(linked)
 (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sdk_report),sdk_object_sha256=sha(sdk_object),relocatable_sha256=sha(linked),remaining_symbols=remaining,application_linked=False,instruction_identity_proven=False),indent=2)+'\n');print('Native manager, port, device and Nordic WDT adapters linked; remaining:',', '.join(remaining))
if __name__=='__main__':main()
