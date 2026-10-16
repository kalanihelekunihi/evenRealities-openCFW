#!/usr/bin/env python3
"""Compile authenticated SDK RTT backend and default registration providers."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-segger-rtt';out.mkdir(exist_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());units=[];inputs={};objects=[]
 for stem,roots in [('SEGGER_RTT',['SEGGER_RTT_WriteNoLock'])]:
  row=next(x for x in sdk['units'] if x['source'].endswith('/'+stem+'.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/(stem+'.o');obj=out/(stem+'-selected.o');dep=out/(stem+'.d');cmd=['clang',*flags,'-O2','-include',str(ROOT/'r1/source-config/sdk/rtt_backend_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True);link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],str(raw),'-o',str(obj)];subprocess.run(link,check=True);subprocess.run(['arm-none-eabi-objcopy','--strip-unneeded',str(obj)],check=True)
  for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
   p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
  transforms=[]
  u,d=undefined_symbols(obj);assert set(u)=={'memcpy'},u;assert '_DoInit' not in subprocess.check_output(['arm-none-eabi-nm',str(obj)],text=True)
  units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,compiled=True,object_transforms=transforms,object_sha256=sha(obj),defined=d,undefined=u));objects.append(obj)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 source=ROOT/'r1/components/board/native_segger_rtt_initialize.c';config=out/'configuration.o';dep=out/'configuration.d';cmd=['clang',*flags,'-O0','-fno-inline','-MD','-MF',str(dep),'-c',str(source),'-o',str(config)];subprocess.run(cmd,check=True);objects.append(config)
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 u,d=undefined_symbols(config);units.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(config),defined=d,undefined=u))
 obj=out/'segger-rtt.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(obj)],check=True);u,d=undefined_symbols(obj);(out/'report.json').write_text(json.dumps(dict(units=units,inputs=inputs,sdk_report_sha256=sha(sp),selected_object_sha256=sha(obj),remaining_symbols=u,scope='Unchanged pinned SEGGER RTT no-lock write with source-owned native initializer; wrapper initialization differences and physical debugger remain gates',configuration_source=str(source.relative_to(ROOT)),configuration_command=cmd,configuration_object_sha256=sha(config),instruction_identity_proven=False),indent=2)+'\n');print('SEGGER RTT compiled; remaining:',u)
if __name__=='__main__':main()
