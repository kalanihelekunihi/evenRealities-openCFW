#!/usr/bin/env python3
"""Select authenticated Nordic SoftDevice-aware NVIC critical-region C bodies."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'sdk-critical';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
    sdk_report=BASE/'application-sdk/report.json';sdk=json.loads(sdk_report.read_text())
    row=next(r for r in sdk['units'] if r['source'].endswith('/app_util_platform.c'))
    source=ROOT/row['source'];assert sha(source)==row['source_sha256']
    obj=out/'app_util_platform.o';dep=out/'app_util_platform.d'
    flags=row['command'][1:row['command'].index('-c')]
    cmd=['clang',*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)]
    subprocess.run(cmd,check=True)
    inputs={}
    for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
        p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
    archive=ROOT/'vendor-cache/r1/sdk.zip'
    assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    linked=out/'critical-only.o'
    subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=app_util_critical_region_enter','--undefined=app_util_critical_region_exit',str(obj),'-o',str(linked)],check=True)
    remaining,defined=undefined_symbols(linked);assert not remaining,remaining
    assert set(defined)=={'app_util_critical_region_enter','app_util_critical_region_exit','nrf_nvic_state'},defined
    undefined,defined=undefined_symbols(obj)
    unit=dict(source=row['source'],source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
    (out/'report.json').write_text(json.dumps(dict(units=[unit],inputs=inputs,sdk_report_sha256=sha(sdk_report),selected_object_sha256=sha(linked),remaining_symbols=remaining,state_address='0x2002c2fc',state_bytes=12,scope='Pinned SoftDevice-aware Nordic critical-region wrappers and shared NVIC state; unused IRQ/privilege helpers excluded from selected object',instruction_identity_proven=False),indent=2)+'\n')
    print('Pinned Nordic critical-region C bodies selected; no unresolved symbols')
if __name__=='__main__':main()
