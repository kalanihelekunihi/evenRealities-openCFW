#!/usr/bin/env python3
"""Compile pinned multi-range iterator/BLE poll and typed recovered observer rows."""
import hashlib,json,subprocess,zipfile,struct
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    layout_path=ROOT/'r1/source-config/ble/observer-layout.json';layout=json.loads(layout_path.read_text());app=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin';assert sha(app)==layout['application_sha256']=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a';blob=app.read_bytes()
    assert list(struct.unpack_from('<3I',blob,int(layout['set_address'],16)-0x27000))==[0x9ca70,0x9ca90,8]
    for i,(first,last) in enumerate(layout['ranges']):assert struct.unpack_from('<2I',blob,0x9ca70+i*8-0x27000)==(int(first,16),int(last,16))
    for row in layout['records']:assert struct.unpack_from('<2I',blob,int(row['address'],16)-0x27000)==(int(layout['handlers'][row['handler']],16)|1,int(layout['contexts'][row['context']],16) if row['context'] else 0)
    out=BASE/'sdk-ble-dispatch';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text());rows=[];objects=[];inputs={str(layout_path.relative_to(ROOT)):sha(layout_path)}
    for suffix in ('nrf_section_iter.c','nrf_sdh_ble.c','native_ble_observers.c'):
        original=next(r for r in sdk['units'] if r['source'].endswith('/'+('nrf_sdh_ble.c' if suffix=='native_ble_observers.c' else suffix)));source=ROOT/('r1/components/board/'+suffix if suffix=='native_ble_observers.c' else original['source']);flags=original['command'][1:original['command'].index('-c')];obj=out/(source.stem+'.o');dep=out/(source.stem+'.d')
        extra=['-DR1_SECTION_ITERATOR_IMPLEMENTATION','-include',str(ROOT/'r1/source-config/sdk/section_legacy_abi.h')] if suffix=='nrf_section_iter.c' else ['-include',str(ROOT/'r1/source-config/sdk/ble_poll_contract.h')]
        command=['clang',*flags,*extra,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True);compiled_sha=sha(obj);transforms=[]
        if suffix=='nrf_sdh_ble.c':
            names={'nrf_sdh_ble_evts_poll':'r1_sdk_ble_events_poll','m_stack_is_enabled':'r1_sdk_ble_stack_enabled','sdh_ble_observers':'r1_sdk_ble_observer_set','sdh_ble_observers_array':'r1_sdk_ble_observer_sections'};transform=['arm-none-eabi-objcopy',*[arg for old,new in names.items() for arg in ('--globalize-symbol='+new,'--redefine-sym',old+'='+new)],str(obj)];subprocess.run(transform,check=True);transforms.append(transform)
        for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,compiled_object_sha256=compiled_sha,object_transforms=transforms,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    selected=out/'ble-dispatch.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in ('r1_sdk_ble_events_poll','r1_sdk_ble_observer_set','r1_sdk_ble_observer_sections','r1_ble_observers_priority1','r1_ble_observers_priority2','r1_ble_observers_priority3')],*map(str,objects),'-o',str(selected)],check=True);remaining,defined=undefined_symbols(selected)
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sdk_path),selected_object_sha256=sha(selected),remaining_symbols=remaining,layout=layout,scope='Pinned SDK multi-range iterator and BLE poll, local returning-error/ABI contract headers, typed priority 1-3 rows; unknown handlers/context objects stay unresolved',instruction_identity_proven=False),indent=2)+'\n');print('BLE poll, legacy iterator and observer rows compiled; remaining:',', '.join(remaining))
if __name__=='__main__':main()
