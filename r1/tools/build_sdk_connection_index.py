#!/usr/bin/env python3
"""Select pinned Nordic index/validity/flag-read and state-reset C bodies."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'sdk-connection-index';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text());rows=[];objects=[];inputs={}
    for suffix in ('ble_conn_state.c','nrf_atflags.c'):
        original=next(r for r in sdk['units'] if r['source'].endswith('/'+suffix));source=ROOT/original['source'];assert sha(source)==original['source_sha256'];flags=original['command'][1:original['command'].index('-c')];obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');command=['clang',*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
        for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=original['source'],source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    selected=out/'connection-index-only.o';subprocess.run(['arm-none-eabi-ld','-r','--gc-sections','--undefined=ble_conn_state_conn_idx','--undefined=ble_conn_state_valid','--undefined=nrf_atflags_get','--undefined=bcs_internal_state_reset','--undefined=ble_conn_state_init',*map(str,objects),'-o',str(selected)],check=True);remaining,defined=undefined_symbols(selected);assert remaining==['memset'],remaining
    assert set(defined)=={'ble_conn_state_conn_idx','ble_conn_state_valid','nrf_atflags_get','bcs_internal_state_reset','ble_conn_state_init'},defined
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sdk_path),selected_object_sha256=sha(selected),remaining_symbols=remaining,state_address='0x2002bdb0',valid_flags_address='0x2002bdb4',candidate_state_bytes=124,authenticated_native_reset_address='0x2002bdb0',authenticated_native_reset_bytes=124,scope='Unchanged Nordic index/validity/bit-read/reset/init bodies; native reset span correlates to SDK state size; remaining field meanings and registry event operations are separate gates',instruction_identity_proven=False),indent=2)+'\n');print('Selected five pinned Nordic C bodies; source memory dependency remains explicit')
if __name__=='__main__':main()
