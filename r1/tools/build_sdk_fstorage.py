#!/usr/bin/env python3
"""Compile unchanged pinned Nordic fstorage facades with native check configuration."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=BASE/'sdk-fstorage';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sp=BASE/'application-sdk/report.json';sdk=json.loads(sp.read_text());row=next(x for x in sdk['units'] if x['source'].endswith('/nrf_fstorage.c'));source=ROOT/row['source'];flags=row['command'][1:row['command'].index('-c')];raw=out/'nrf_fstorage.o';obj=out/'fstorage.o';dep=out/'nrf_fstorage.d';cmd=['clang',*flags,'-include',str(ROOT/'r1/source-config/sdk/fstorage_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(raw)];subprocess.run(cmd,check=True)
 link=['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in ('nrf_fstorage_init','nrf_fstorage_erase','nrf_fstorage_write','nrf_fstorage_is_busy')],str(raw),'-o',str(obj)];subprocess.run(link,check=True)
 inputs={}
 for n in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
  p=Path(n);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else n]=sha(p)
 archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
 with zipfile.ZipFile(archive) as bundle:
  prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
  for p,d in inputs.items():
   if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
 u,d=undefined_symbols(obj);assert set(u)=={'__start_fs_data','__stop_fs_data'},u
 (out/'report.json').write_text(json.dumps(dict(units=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=link,compile_command=cmd,compiled=True,object_sha256=sha(obj),defined=d,undefined=u)],inputs=inputs,sdk_report_sha256=sha(sp),scope='Unchanged SDK fstorage init/erase/write/busy facades; native disabled parameter checks/asserts, final fs_data extent and underlying API implementation remain requirements',instruction_identity_proven=False),indent=2)+'\n');print('Four pinned SDK fstorage facades compiled')
if __name__=='__main__':main()
