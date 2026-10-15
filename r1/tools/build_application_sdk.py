#!/usr/bin/env python3
"""Compile application-side Nordic providers; keep configuration gates visible."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import struct
import zipfile
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols

ROOT=Path(__file__).resolve().parents[2]
SDK_SHA='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
EXTRA=[
'components/ble/ble_link_ctx_manager/ble_link_ctx_manager.c',
'components/ble/ble_services/ble_dfu/ble_dfu.c','components/ble/ble_services/ble_dfu/ble_dfu_unbonded.c',
'components/ble/nrf_ble_qwr/nrf_ble_qwr.c','components/libraries/bootloader/dfu/nrf_dfu_svci.c',
'components/libraries/balloc/nrf_balloc.c','components/libraries/memobj/nrf_memobj.c',
'components/libraries/ringbuf/nrf_ringbuf.c','components/libraries/log/src/nrf_log_frontend.c',
'components/libraries/log/src/nrf_log_str_formatter.c','components/libraries/log/src/nrf_log_backend_rtt.c',
'components/libraries/log/src/nrf_log_backend_serial.c','components/libraries/log/src/nrf_log_default_backends.c',
'external/fprintf/nrf_fprintf.c','external/fprintf/nrf_fprintf_format.c',
'components/libraries/pwr_mgmt/nrf_pwr_mgmt.c','modules/nrfx/drivers/src/nrfx_nfct.c',
'modules/nrfx/drivers/src/nrfx_pdm.c','modules/nrfx/drivers/src/nrfx_timer.c']


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sdk=ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560';archive=sdk.parent/'sdk.zip'
    assert sha(archive)==SDK_SHA
    output=ROOT/'r1/research/source-build/application-sdk';output.mkdir(parents=True,exist_ok=True)
    (output/'report.json').unlink(missing_ok=True)
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if member.is_dir():continue
            relative=Path(member.filename).relative_to(sdk.name)
            assert hashlib.sha256(bundle.read(member)).hexdigest()==sha(sdk/relative),relative
    template=sdk/'examples/ble_peripheral/ble_app_hrs_freertos/pca10056/s140/config/sdk_config.h'
    (output/'r1_sdk_example_defaults.h').write_bytes(template.read_bytes())
    svci_original=sdk/'components/libraries/svc/nrf_svci.h'
    svci_patch=output/'nrf_svci_clang.h'
    contents=svci_original.read_text()
    assert contents.count('ldr r12, =%0')==1 and contents.count('ldr.w r12, =%0')==1
    svci_patch.write_text(contents.replace('ldr r12, =%0', 'ldr r12, =%c0').replace('ldr.w r12, =%0', 'ldr.w r12, =%c0'))
    seed=(ROOT/'r1/config-recovered/sdk-source-list.mk').read_text()
    source_block=seed.split('SRC_FILES +=',1)[1].split('INC_FOLDERS +=',1)[0]
    sources=list(dict.fromkeys(re.findall(r'\$\(SDK_ROOT\)/([^\s\\]+\.c)',source_block)+EXTRA))
    # RTOS sources are compiled under the dedicated, pinned RTOS candidate target.
    sources=[path for path in sources if not path.startswith('external/freertos/')]
    includes_block=seed.split('INC_FOLDERS +=',1)[1].split('OPT :=',1)[0]
    includes=[sdk/path for path in re.findall(r'\$\(SDK_ROOT\)/([^\s\\]+)',includes_block)]
    includes += sorted({(sdk/path).parent for path in EXTRA})
    includes += [sdk/'components/libraries/log',sdk/'components/libraries/log/src',sdk/'components/libraries/mutex',
                 sdk/'components/libraries/strerror',sdk/'components/libraries/bootloader',
                 sdk/'components/libraries/bootloader/ble_dfu',sdk/'components/libraries/bootloader/dfu',sdk/'components/libraries/svc',
                 sdk/'components/libraries/stack_info',sdk/'components/libraries/mem_manager',
                 sdk/'components/libraries/queue',sdk/'components/libraries/scheduler',
                 sdk/'components/libraries/atomic_flags',sdk/'components/libraries/atomic_fifo',
                 ROOT/'third-party/upstream/freertos-kernel/include',
                 sdk/'external/freertos/portable/GCC/nrf52',sdk/'external/freertos/portable/CMSIS/nrf52',
                 ROOT/'r1/source-config/rtos']
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
           '-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-std=c11','-Os',
           '-ffunction-sections','-fdata-sections','-DNRF52840_XXAA','-DFLOAT_ABI_HARD',
           '-DNRF_SD_BLE_API_VERSION=7','-DNRF_DFU_SVCI_ENABLED','-DNRF_DFU_TRANSPORT_BLE=1','-DS140','-DSOFTDEVICE_PRESENT','-DFREERTOS',
           '-DCONFIG_NFCT_PINS_AS_GPIOS','-DCONFIG_GPIO_AS_PINRESET',
           '-I'+str(ROOT/'r1/source-config/sdk'),'-I'+str(output),'-include',str(svci_patch),
           '-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),
           *['-I'+str(p) for p in dict.fromkeys(includes)]]
    # Authenticate the vector selections that justify enabled driver instances.
    application=ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin'
    image=application.read_bytes()
    assert sha(application)=='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    device=(sdk/'modules/nrfx/mdk/nrf52840.h').read_text()
    entries={'RTC2':0x31751,'TIMER0':0x274a3,'TIMER1':0x274a3,'TIMER2':0x33829,
             'TIMER3':0x274a3,'TIMER4':0x3383d,'NFCT':0x3060d,'PDM':0x309dd}
    vectors={}
    for peripheral,expected in entries.items():
        irq=int(re.search(r'\b'+peripheral+r'_IRQn\s*=\s*(\d+)',device)[1])
        pointer=struct.unpack_from('<I',image,4*(16+irq))[0]
        assert pointer==expected,(peripheral,hex(pointer))
        vectors[peripheral]=dict(irq=irq,vector=hex(pointer),vector_slot=hex(0x27000+4*(16+irq)))
    expected_config={'NRFX_GPIOTE_CONFIG_NUM_OF_LOW_POWER_EVENTS':8,'NRFX_GPIOTE_CONFIG_IRQ_PRIORITY':6,'NRFX_RTC_ENABLED':1,'NRFX_RTC0_ENABLED':0,'NRFX_RTC1_ENABLED':0,'NRFX_RTC2_ENABLED':1,
                     'NRFX_TIMER_ENABLED':1,'NRFX_TIMER0_ENABLED':0,'NRFX_TIMER1_ENABLED':0,
                     'NRFX_TIMER2_ENABLED':1,'NRFX_TIMER3_ENABLED':0,'NRFX_TIMER4_ENABLED':1,
                     'NRFX_NFCT_ENABLED':1,'NRFX_PDM_ENABLED':1,'NRF_LOG_ENABLED':1,'NRF_LOG_DEFERRED':1,
                     'NRF_BLE_QWR_MAX_ATTR':0,'NRF_DFU_BLE_BUTTONLESS_SUPPORTS_BONDS':0,
                     'NRF_PWR_MGMT_CONFIG_USE_SCHEDULER':0,'SEGGER_RTT_CONFIG_BUFFER_SIZE_DOWN':64}
    probe=output/'configuration_probe.c'
    probe.write_text('#include "nrfx.h"\n'+''.join(f'_Static_assert({name} == {value}, "{name}");\n' for name,value in expected_config.items()))
    probe_obj=output/'configuration_probe.o'
    subprocess.run(['clang',*flags,'-c',str(probe),'-o',str(probe_obj)],check=True)
    rows=[]
    for i,relative in enumerate(sources):
        original=sdk/relative;source=original
        if original.name=='app_error_handler_gcc.c':
            source=output/'app_error_handler_gcc_clang.c'
            # Keep the SDK license and body; change only the literal operand's
            # formatting modifier so Clang does not print an invalid '=#16385'.
            contents=original.read_text()
            assert contents.count('ldr r0, =%4')==1
            source.write_text(contents.replace('ldr r0, =%4                    ', 'ldr r0, =%c4                   '))
        obj=output/f'{i:02d}_{original.stem}.o';obj.unlink(missing_ok=True)
        command=['clang',*flags,'-c',str(source),'-o',str(obj)]
        result=subprocess.run(command,capture_output=True,text=True)
        row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),original_source=str(original.relative_to(ROOT)),original_source_sha256=sha(original),command=command,
                 compiled=result.returncode==0,diagnostics=result.stderr)
        if row['compiled']:
            undefined,defined=undefined_symbols(obj);body_symbols=functions(obj)
            row.update(undefined=undefined,defined=defined,object_sha256=sha(obj),
                       emitted_function_count=len(body_symbols),emitted_code_bytes=sum(size for _,size in body_symbols))
        rows.append(row)
    svci_check=None
    if all(row['compiled'] for row in rows):
        svci_row=next(row for row in rows if row['original_source'].endswith('/ble_dfu_unbonded.c'))
        object_path=Path(svci_row['command'][-1])
        stub=output/'svci-stub.bin'
        subprocess.run(['arm-none-eabi-objcopy','-O','binary',
                        '--only-section=.text.svci_nrf_dfu_set_adv_name_svci_async_init',
                        str(object_path),str(stub)],check=True)
        # mov.w r12,#3; svc #0; bx lr. The Clang adaptation must preserve
        # the indirect supervisor-call ABI, not turn it into a normal call.
        assert stub.read_bytes()==bytes.fromhex('4ff0030c00df7047')
        svci_check=dict(scope='candidate supervisor-call ABI only, not stock instruction identity',
                        r12_function_number=3,svc_immediate=0,stub_sha256=sha(stub),bytes=stub.stat().st_size)
    definitions={s for row in rows for s in row.get('defined',[])}
    report=dict(schema=1,sdk_archive_sha256=SDK_SHA,application_sha256=sha(application),vectors=vectors,effective_configuration_assertions=expected_config,configuration_probe_sha256=sha(probe),units=rows,compiled=sum(row['compiled'] for row in rows),total=len(rows),
                nonempty_units=sum(row.get('emitted_function_count',0)>0 for row in rows),
                unresolved=sorted({s for row in rows for s in row.get('undefined',[])}-definitions),
                svci_abi_check=svci_check,compiler_adaptations={'svci_original_sha256':sha(svci_original),'svci_compiled_header_sha256':sha(svci_patch),'description':'Clang constant operand formatting only; retained SVC instruction and R12 function number.'},
                configuration={str(p.relative_to(ROOT)):sha(p) for p in
                               [ROOT/'r1/source-config/sdk/sdk_config.h',ROOT/'r1/config-recovered/sdk_config.h',template]},
                compiler_version=subprocess.check_output(['clang','--version'],text=True),
                image_linked=False,stock_configuration_proven=False,byte_identity_proven=False,
                limitations=['Unspecified values use authenticated SDK example defaults; they are not admitted stock configuration.',
                             'Compiled units with no emitted functions are reported separately and do not close provider bodies.',
                             'GCC-specific error-handler implementation is a candidate only; stock uses ArmCC.',
                             'Peripheral driver compilation does not establish initialization or physical operation.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Application SDK units compiled: {report['compiled']}/{report['total']}; {report['nonempty_units']} emit functions")
    for row in rows:
        if not row['compiled']:print(row['source']+'\n'+row['diagnostics'][:1600])
    print('Empty units:',[Path(row['source']).name for row in rows if row['compiled'] and not row.get('emitted_function_count')])
    return 0 if all(row['compiled'] for row in rows) else 1


if __name__=='__main__':raise SystemExit(main())
