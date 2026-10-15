#!/usr/bin/env python3
"""Compile authenticated unchanged Nordic link-context lookup provider."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'sdk-link-context';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
    sdk_report=BASE/'application-sdk/report.json';sdk=json.loads(sdk_report.read_text())
    row=next(r for r in sdk['units'] if r['source'].endswith('/ble_link_ctx_manager.c'))
    source=ROOT/row['source'];assert sha(source)==row['source_sha256']
    obj=out/'blcm_link_ctx_get.o';dep=out/'blcm_link_ctx_get.d'
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
    undefined,defined=undefined_symbols(obj)
    unit=dict(source=row['source'],source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
    (out/'report.json').write_text(json.dumps(dict(units=[unit],inputs=inputs,sdk_report_sha256=sha(sdk_report),remaining_symbols=undefined,provider_aliases={'r1_native_bae8_context_get':'blcm_link_ctx_get'},scope='Unchanged pinned Nordic link-context lookup; connection-index provider and actual storage configuration remain dependencies',instruction_identity_proven=False),indent=2)+'\n')
    print('Pinned Nordic link-context C provider compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()
