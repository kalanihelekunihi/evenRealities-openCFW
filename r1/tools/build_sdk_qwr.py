#!/usr/bin/env python3
"""Compile unchanged pinned queued-write SDK and authenticated three instances."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'sdk-qwr';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text());rows=[];objects=[];inputs={}
    for suffix in ('nrf_ble_qwr.c','native_qwr_contexts.c'):
        original=next(r for r in sdk['units'] if r['source'].endswith('/nrf_ble_qwr.c'));source=ROOT/('r1/components/board/'+suffix if suffix=='native_qwr_contexts.c' else original['source']);flags=original['command'][1:original['command'].index('-c')];obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');command=['clang',*flags,'-include',str(ROOT/'r1/source-config/sdk/qwr_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
        for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
        compiled_sha=sha(obj);transforms=[]
        if suffix=='nrf_ble_qwr.c':
            transform=['arm-none-eabi-objcopy','--globalize-symbol=r1_sdk_qwr_user_mem_reply','--redefine-sym','user_mem_reply=r1_sdk_qwr_user_mem_reply',str(obj)];subprocess.run(transform,check=True);transforms.append(transform)
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),compiled_object_sha256=compiled_sha,object_transforms=transforms,undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    selected=out/'qwr.o';roots=('nrf_ble_qwr_init','nrf_ble_qwr_conn_handle_assign','nrf_ble_qwr_on_ble_evt','r1_sdk_qwr_user_mem_reply','r1_ble_qwr_context_a','r1_ble_qwr_context_b','r1_ble_qwr_context_c')
    subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],*map(str,objects),'-o',str(selected)],check=True);remaining,defined=undefined_symbols(selected);assert not remaining,remaining
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sdk_path),selected_object_sha256=sha(selected),remaining_symbols=remaining,context_addresses={n:hex(0x20007e40+i*12) for i,n in enumerate(roots[-3:])},bool_representation_policy='Canonical C bool 0/1 verified; noncanonical byte 2 diverges from stock and remains an explicit compiler-domain gate',context_bytes_each=12,native_initializer_loop='0x0004df3c..0x0004df56',scope='Unchanged pinned Nordic QWR C, zero attribute policy, three typed contexts; callback initialization remains the production caller responsibility',instruction_identity_proven=False),indent=2)+'\n');print('Queued-write provider and three typed contexts compiled without unresolved providers')
if __name__=='__main__':main()
