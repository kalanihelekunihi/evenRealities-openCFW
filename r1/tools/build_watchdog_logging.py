#!/usr/bin/env python3
"""Build unmodified Nordic WDT/strerror with recovered R1 log integration."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'watchdog-logging';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
    parent=BASE/'watchdog-startup/report.json';base=json.loads(parent.read_text());sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text())
    rows=list(base['units']);objects=[];inputs=dict(base['inputs'])
    for row in rows:
        obj=Path(row['command'][-1]);assert sha(obj)==row['object_sha256'];assert sha(ROOT/row['source'])==row['source_sha256'];objects.append(obj)
    for suffix in ('nrfx_wdt.c','nrf_strerror.c'):
        row=next(r for r in sdk['units'] if r['source'].endswith('/'+suffix));source=ROOT/row['source'];assert sha(source)==row['source_sha256']
        obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');flags=row['command'][1:row['command'].index('-c')]
        command=['clang','-I'+str(ROOT/'r1/source-config/sdk-wdt'),*flags,'-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)]
        subprocess.run(command,check=True)
        for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=row['source'],source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    getter_report=BASE/'board-seams/report.json';getter=json.loads(getter_report.read_text())['units'][0];getter_obj=Path(getter['command'][-1]);assert sha(getter_obj)==getter['object_sha256']
    selected=out/'mode-getter-only.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=r1_structured_log_mode_get',str(getter_obj),'-o',str(selected)],check=True)
    linked=out/'native-watchdog-logging.o';subprocess.run(['arm-none-eabi-ld','-r',*map(str,objects),'-o',str(linked)],check=True);remaining,_=undefined_symbols(linked)
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,parent_report_sha256=sha(parent),sdk_report_sha256=sha(sdk_path),getter_report_sha256=sha(getter_report),selected_getter_sha256=sha(selected),relocatable_sha256=sha(linked),remaining_symbols=remaining,scope='Unchanged Nordic WDT/strerror, recovered R1 WDT-only log header, original native manager/port/device and actual source mode getter',instruction_identity_proven=False),indent=2)+'\n')
    print('Watchdog log-policy variant compiled; remaining:',', '.join(remaining))
if __name__=='__main__':main()
