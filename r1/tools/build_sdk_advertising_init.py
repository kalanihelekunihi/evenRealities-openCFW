#!/usr/bin/env python3
"""Compile unchanged pinned advertising providers and typed compatible contexts."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];BASE=ROOT/'r1/research/source-build';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=BASE/'sdk-advertising-init';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True);sdk_path=BASE/'application-sdk/report.json';sdk=json.loads(sdk_path.read_text());rows=[];objects=[];inputs={}
    for suffix in ('ble_advertising.c','ble_advdata.c','native_advertising_contexts.c'):
        original=next(r for r in sdk['units'] if r['source'].endswith('/'+('ble_advdata.c' if suffix=='ble_advdata.c' else 'ble_advertising.c')));source=ROOT/('r1/components/board/'+suffix if suffix=='native_advertising_contexts.c' else original['source']);flags=original['command'][1:original['command'].index('-c')];obj=out/(source.stem+'.o');dep=out/(source.stem+'.d');command=['clang',*flags,'-fno-inline-functions','-include',str(ROOT/'r1/source-config/sdk/advertising_init_contract.h'),'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
        for name in dep.read_text().replace('\\\n',' ').split(':',1)[1].split():
            p=Path(name);inputs[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else name]=sha(p)
        compiled_sha=sha(obj);transforms=[]
        if suffix=='ble_advertising.c':
            names={'flags_set':'r1_sdk_adv_flags_set','phy_is_valid':'r1_sdk_adv_phy_is_valid','use_whitelist':'r1_sdk_adv_use_whitelist','adv_set_data_size_max_get':'r1_sdk_adv_data_size_max_get'}
            transform=['arm-none-eabi-objcopy',*[arg for old,new in names.items() for arg in ('--globalize-symbol='+new,'--redefine-sym',old+'='+new)],str(obj)];subprocess.run(transform,check=True);transforms.append(transform)
        if suffix=='ble_advdata.c':
            names={'ble_device_addr_encode':'r1_sdk_adv_device_addr_encode','conn_int_encode':'r1_sdk_adv_conn_int_encode','manuf_specific_data_encode':'r1_sdk_adv_manuf_encode','service_data_encode':'r1_sdk_adv_service_encode','name_encode':'r1_sdk_adv_name_encode','uuid_list_sized_encode':'r1_sdk_adv_uuid_list_sized_encode'}
            transform=['arm-none-eabi-objcopy',*[arg for old,new in names.items() for arg in ('--globalize-symbol='+new,'--redefine-sym',old+'='+new)],str(obj)];subprocess.run(transform,check=True);transforms.append(transform)
        undefined,defined=undefined_symbols(obj);rows.append(dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,object_sha256=sha(obj),compiled_object_sha256=compiled_sha,object_transforms=transforms,undefined=undefined,defined=defined,emitted_function_count=len(functions(obj))));objects.append(obj)
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):])).hexdigest()==digest,path
    selected=out/'advertising.o';roots=('ble_advertising_init','ble_advdata_encode','r1_sdk_adv_device_addr_encode','r1_sdk_adv_conn_int_encode','r1_sdk_adv_manuf_encode','r1_sdk_adv_service_encode','r1_sdk_adv_name_encode','r1_sdk_adv_uuid_list_sized_encode','r1_sdk_adv_data_size_max_get','ble_advertising_on_ble_evt','ble_advertising_start','ble_advertising_conn_cfg_tag_set','ble_advertising_modes_config_set','r1_sdk_adv_flags_set','r1_sdk_adv_phy_is_valid','r1_sdk_adv_use_whitelist','ble_advdata_parse','ble_advdata_search','r1_ble_advertising_context_a','r1_ble_advertising_context_b')
    subprocess.run(['arm-none-eabi-ld','-r','--gc-sections',*['--undefined='+n for n in roots],*map(str,objects),'-o',str(selected)],check=True);remaining,defined=undefined_symbols(selected);assert set(remaining)<=set(('memcpy','memset','__aeabi_memcpy','__aeabi_memcpy4')),remaining
    (out/'report.json').write_text(json.dumps(dict(units=rows,inputs=inputs,sdk_report_sha256=sha(sdk_path),selected_object_sha256=sha(selected),remaining_symbols=remaining,context_addresses={'r1_ble_advertising_context_a':'0x20007e64','r1_ble_advertising_context_b':'0x200082b0'},context_bytes_each=1076,initialization_provider_selected=True,scope='Unchanged pinned Nordic advertising observer/start/config and helpers; typed compatible contexts; actual init and data encoding selected; product configuration and live controller remain gates',instruction_identity_proven=False),indent=2)+'\n');print('Advertising initialization/encoding variant compiled with explicit controller and product-configuration gates')
if __name__=='__main__':main()
