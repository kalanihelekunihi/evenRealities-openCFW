#!/usr/bin/env python3
"""Compile authenticated GATT initialization and its typed context."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'sdk-gatt';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text());rows=[];objects=[];inputs={}
    for suffix in ('nrf_ble_gatt.c','native_gatt_context.c'):
        original=next(r for r in sdk['units'] if r['source'].endswith('/nrf_ble_gatt.c'));source=ROOT/('r1/components/board/'+suffix if suffix=='native_gatt_context.c' else original['source']);flags=original['command'][1:original['command'].index('-c')];obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');command=['clang',*flags,'-fno-inline-functions','-include',str(ROOT/'r1/source-config/sdk/gatt_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
        for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
        compiled_sha=sha(obj);transforms=[]
        if suffix=='nrf_ble_gatt.c':
            transform=['arm-none-eabi-objcopy','--globalize-symbol=r1_sdk_gatt_link_init','--redefine-sym','link_init=r1_sdk_gatt_link_init',str(obj)];subprocess.run(transform,check=True);transforms.append(transform)
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),compiled_object_sha256=compiled_sha,object_transforms=transforms,undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    selected=out/'gatt-init.o';roots=('nrf_ble_gatt_init','r1_sdk_gatt_link_init','r1_ble_gatt_context')
    subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],*map(str,objects),'-o',str(selected)],check=True);remaining,defined=undefined_symbols(selected);assert not remaining,remaining
    assert set(defined)==set(roots),defined
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sdk_path),selected_object_sha256=sha(selected),remaining_symbols=remaining,context_address='0x20007e1c',context_bytes=36,link_count_sum=3,mtu_default=247,data_length_default=251,role_split_proven=False,observer_selected=False,scope='Unchanged pinned SDK init/link-init and one source-owned context; product observer differences remain explicit',instruction_identity_proven=False),indent=2)+'\n');print('GATT init/link-init and typed context compiled; observer deliberately remains unresolved pending product differences')
if __name__=='__main__':main()
