#!/usr/bin/env python3
"""Build native GATT product policy with authenticated Nordic types."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'native-gatt';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
    sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text());row=next(r for r in sdk['units'] if r['source'].endswith('/nrf_ble_gatt.c'));flags=row['command'][1:row['command'].index('-c')]
    source=ROOT/'r1/components/board/native_gatt_observer.c';obj=out/'native_gatt_observer.o';dep=out/'native_gatt_observer.d';command=['clang',*flags,'-include',str(ROOT/'r1/source-config/sdk/gatt_contract.h'),'-Wall','-Wextra','-Werror','-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
    inputs={}
    for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
        p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
    reference=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/components/ble/nrf_ble_gatt/nrf_ble_gatt.c';inputs[str(reference.relative_to(ROOT))]=sha(reference)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    undefined,defined=undefined_symbols(obj);unit=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
    (out/'report.json').write_text(json.dumps(dict(units=[unit],inputs=inputs,sdk_report_sha256=sha(sdk_path),upstream_reference=str(reference.relative_to(ROOT)),scope='R1 GATT observer and data-length/MTU helpers reconstructed against native routing; SDK ABI types and initialization reused, actual SVC and dual-log policy',observer_contract_proven=False,instruction_identity_proven=False),indent=2)+'\n');print('Native GATT observer/helpers compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()
