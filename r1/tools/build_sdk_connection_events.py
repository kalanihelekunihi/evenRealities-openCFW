#!/usr/bin/env python3
"""Select pinned Nordic registry event writer and shared read/reset/atomic providers."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'sdk-connection-events';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text());rows=[];objects=[];inputs={}
    for suffix in ('ble_conn_state.c','nrf_atflags.c','nrf_atomic.c'):
        original=next(r for r in sdk['units'] if r['source'].endswith('/'+suffix));source=ROOT/original['source'];assert sha(source)==original['source_sha256'];flags=original['command'][1:original['command'].index('-c')];obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');command=['clang',*flags,*(['-include',str(ROOT/'r1/source-config/sdk/connection_events.h')] if suffix=='ble_conn_state.c' else []),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
        for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
        compiled_sha=sha(obj);transforms=[]
        if suffix=='ble_conn_state.c':
            transform=['arm-none-eabi-objcopy','--globalize-symbol=r1_sdk_connection_event','--globalize-symbol=r1_sdk_connection_observer','--redefine-sym','ble_evt_handler=r1_sdk_connection_event','--redefine-sym','m_ble_evt_observer=r1_sdk_connection_observer',str(obj)];subprocess.run(transform,check=True);transforms.append(transform)
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=original['source'],source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),compiled_object_sha256=compiled_sha,object_transforms=transforms,undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    selected=out/'connection-events.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=ble_conn_state_conn_idx','--undefined=ble_conn_state_valid','--undefined=nrf_atflags_get','--undefined=bcs_internal_state_reset','--undefined=ble_conn_state_init','--undefined=r1_sdk_connection_event','--undefined=r1_sdk_connection_observer',*map(str,objects),'-o',str(selected)],check=True);remaining,defined=undefined_symbols(selected);assert set(remaining)<=set(('memset','memcpy','__aeabi_memcpy4','r1_adc_error')),remaining
    assert set(defined)=={'ble_conn_state_conn_idx','ble_conn_state_valid','nrf_atflags_get','bcs_internal_state_reset','ble_conn_state_init','r1_sdk_connection_event','conn_handle_list_get','nrf_atflags_set','nrf_atflags_clear','nrf_atomic_u32_and','nrf_atomic_u32_or','r1_sdk_connection_observer'},defined
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sdk_path),selected_object_sha256=sha(selected),remaining_symbols=remaining,state_address='0x2002bdb0',valid_flags_address='0x2002bdb4',candidate_state_bytes=124,observer_address='0x000c4568',observer_bytes=8,observer_priority_section='.sdh_ble_observers0',authenticated_native_reset_address='0x2002bdb0',authenticated_native_reset_bytes=124,scope='Unchanged Nordic registry event/read/reset/atomic source; R1 returning error macro and callback symbol export; single shared state instance, actual event routing remains separate',instruction_identity_proven=False),indent=2)+'\n');print('Registry event/read/reset/atomic provider selected; memory and returning-error dependencies remain explicit')
if __name__=='__main__':main()
