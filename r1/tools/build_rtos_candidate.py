#!/usr/bin/env python3
"""Compile the pinned R1 kernel/wrapper and R1-owned static memory callbacks."""
import hashlib
import json
from pathlib import Path
import subprocess
from build_source_candidates import undefined_symbols

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    sdk = ROOT/'vendor-cache/r1/nRF5_SDK_17.1.0_ddde560'
    sdk_archive=sdk.parent/'sdk.zip'
    assert sha(sdk_archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    kernel = ROOT/'third-party/upstream/freertos-kernel'
    cmsis = ROOT/'third-party/upstream/cmsis-freertos'
    pins = {kernel:'def7d2df2b0506d3d249334974f51e427c17a41c',
            cmsis:'d213f261b5be6bb29a7cce8b84071706b72f4d53',
            ROOT/'third-party/upstream/cmsis-5-590':'2b7495b8535bdcb306dac29b9ded4cfb679d7e5c'}
    for tree, pin in pins.items():
        assert (tree/'.git').exists()
        assert subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()==pin
        assert not subprocess.check_output(['git','-C',str(tree),'status','--porcelain'],text=True).strip()
    includes = [ROOT/'r1/source-config/rtos',ROOT/'r1/config-recovered',kernel/'include',
                sdk/'external/freertos/portable/GCC/nrf52',sdk/'external/freertos/portable/CMSIS/nrf52',
                cmsis/'CMSIS/RTOS2/FreeRTOS/Include',sdk/'components/toolchain/cmsis/include',
                sdk/'components/softdevice/common',sdk/'components/libraries/experimental_section_vars',sdk/'components/libraries/util',sdk/'components/libraries/delay',sdk/'components/libraries/atomic',
                sdk/'modules/nrfx/mdk',sdk/'modules/nrfx',sdk/'modules/nrfx/hal',sdk/'modules/nrfx/drivers/include',
                sdk/'integration/nrfx',sdk/'integration/nrfx/legacy',
                sdk/'components/softdevice/s140/headers',sdk/'components/softdevice/s140/headers/nrf52']
    # CMSIS RTOS2 API headers come from the separately pinned CMSIS 5 tree.
    cmsis_headers=ROOT/'third-party/upstream/cmsis-5-590/CMSIS/RTOS2/Include'
    includes.append(cmsis_headers)
    sources=[kernel/name for name in ('tasks.c','list.c','queue.c','timers.c','event_groups.c','stream_buffer.c','portable/MemMang/heap_4.c')]
    sources += [sdk/'external/freertos/portable/GCC/nrf52/port.c',
                sdk/'external/freertos/portable/CMSIS/nrf52/port_cmsis.c',
                sdk/'external/freertos/portable/CMSIS/nrf52/port_cmsis_systick.c',
                cmsis/'CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c',
                ROOT/'r1/components/rtos/static_task_memory.c']
    output=ROOT/'r1/research/source-build/rtos';output.mkdir(parents=True,exist_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
           '-ffreestanding','-fno-strict-aliasing','-std=c11','-Os','-ffunction-sections','-fdata-sections',
           '-DNRF52840_XXAA','-DSOFTDEVICE_PRESENT','-DNRF_SD_BLE_API_VERSION=7','-DS140',
           '-DFREERTOS','-DFLOAT_ABI_HARD',
           '-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include'),
           *['-I'+str(p) for p in includes]]
    probe=output/'layout_probe.c'
    probe.write_text('#include "FreeRTOS.h"\nchar r1_tcb_extent[sizeof(StaticTask_t)];\n')
    probe_obj=output/'layout_probe.o'
    subprocess.run(['clang',*flags,'-c',str(probe),'-o',str(probe_obj)],check=True)
    symbols=subprocess.check_output(['arm-none-eabi-nm','-S',str(probe_obj)],text=True)
    tcb_bytes=int(next(line.split()[1] for line in symbols.splitlines() if line.endswith(' r1_tcb_extent')),16)
    rows=[]
    for i,source in enumerate(sources):
        obj=output/f'{i:02d}_{source.stem}.o';command=['clang',*flags,'-c',str(source),'-o',str(obj)]
        result=subprocess.run(command,capture_output=True,text=True)
        row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,
                 compiled=result.returncode==0,diagnostics=result.stderr)
        if row['compiled']:
            undefined,defined=undefined_symbols(obj);row.update(undefined=undefined,defined=defined,object_sha256=sha(obj))
        else:obj.unlink(missing_ok=True)
        rows.append(row)
    defined={s for row in rows for s in row.get('defined',[])}
    report=dict(schema=1,sdk_archive_sha256=sha(sdk_archive),compiler_version=subprocess.check_output(['clang','--version'],text=True),pins={str(tree.relative_to(ROOT)):pin for tree,pin in pins.items()},
                units=rows,compiled=sum(row['compiled'] for row in rows),total=len(rows),
                unresolved=sorted({s for row in rows for s in row.get('undefined',[])}-defined),
                candidate_tcb_bytes=tcb_bytes,stock_control_reservation_bytes=112,
                layout_probe_source_sha256=sha(probe),image_linked=False,stock_configuration_proven=False,byte_identity_proven=False,
                configuration_sha256=sha(ROOT/'r1/source-config/rtos/FreeRTOSConfig.h'))
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"RTOS candidate units compiled: {report['compiled']}/{report['total']}")
    for row in rows:
        if not row['compiled']:print(row['source']+'\n'+row['diagnostics'][:2200])
    return 0 if all(row['compiled'] for row in rows) else 1


if __name__=='__main__':raise SystemExit(main())
