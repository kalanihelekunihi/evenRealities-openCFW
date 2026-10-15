#!/usr/bin/env python3
"""Compile native named GPIO records without inventing missing event bodies."""
import hashlib,json,subprocess
from pathlib import Path
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols
ROOT=Path(__file__).resolve().parents[2];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'r1/research/source-build/gpio';out.mkdir(exist_ok=True);(out/'report.json').unlink(missing_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard','-std=c11','-Os','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-fno-delete-null-pointer-checks','-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror','-I'+str(ROOT/'r1/reconstructed')]
    sdk_report=json.loads((ROOT/'r1/research/source-build/application-sdk/report.json').read_text())
    setup=sdk_report['units'][0]['command'];flags=setup[1:setup.index('-c')]+['-Wall','-Wextra','-Werror','-I'+str(ROOT/'r1/reconstructed')]
    source=ROOT/'r1/components/gpio/stock_named_gpio.c';obj=out/'stock_named_gpio.o';dep=out/'stock_named_gpio.d';cmd=['clang',*flags,'-MD','-MF',str(dep),'-c',str(source),'-o',str(obj)];subprocess.run(cmd,check=True);undefined,defined=undefined_symbols(obj)
    row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=cmd,compiled=True,object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))
    dependencies=dep.read_text().replace('\\\n',' ').split(':',1)[1].split()
    inputs={(str(Path(p).relative_to(ROOT)) if Path(p).is_relative_to(ROOT) else p):sha(Path(p)) for p in dependencies}
    import zipfile
    archive=ROOT/'vendor-cache/r1/sdk.zip'
    assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for path,digest in inputs.items():
            if path.startswith(prefix):
                member='nRF5_SDK_17.1.0_ddde560/'+path[len(prefix):]
                assert hashlib.sha256(bundle.read(member)).hexdigest()==digest,path
    headers={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'r1/components/gpio/stock_named_gpio.h',ROOT/'r1/components/registry/stock_registry.h',ROOT/'r1/reconstructed/generic_device_registry/generic_device_registry.h']}
    gpiote=next(row for row in sdk_report['units'] if row['source'].endswith('/nrfx_gpiote.c'))
    gpiote_object=Path(gpiote['command'][-1]);assert sha(gpiote_object)==gpiote['object_sha256']
    assert sha(ROOT/gpiote['source'])==gpiote['source_sha256']
    probe=out/'gpiote_layout_probe.c'
    probe.write_text('#include <stddef.h>\n#include "'+str(ROOT/gpiote['source'])+'"\n'+
        '_Static_assert(NRFX_GPIOTE_CONFIG_NUM_OF_LOW_POWER_EVENTS==8,"low power slots");\n'+
        '_Static_assert(sizeof(gpiote_control_block_t)==128,"control extent");\n'+
        '_Static_assert(offsetof(gpiote_control_block_t,pin_assignments)==64,"assignments");\n'+
        '_Static_assert(offsetof(gpiote_control_block_t,port_handlers_pins)==112,"port handlers");\n'+
        '_Static_assert(offsetof(gpiote_control_block_t,configured_pins)==120,"configured pins");\n'+
        '_Static_assert(offsetof(gpiote_control_block_t,state)==126,"state");\n')
    subprocess.run(['clang',*flags,'-fsyntax-only',str(probe)],check=True)
    integrated=ROOT/'r1/research/source-build/i2c5/st25-i2c5-registry.o'
    i2c_report=json.loads((integrated.parent/'report.json').read_text());assert sha(integrated)==i2c_report['relocatable_sha256']
    linked=out/'gpio-native-integration.o'
    subprocess.run(['arm-none-eabi-ld','-r',str(obj),str(integrated),str(gpiote_object),'-o',str(linked)],check=True)
    remaining,_=undefined_symbols(linked)
    integration=dict(relocatable_sha256=sha(linked),i2c5_report_sha256=sha(integrated.parent/'report.json'),
        sdk_report_sha256=sha(ROOT/'r1/research/source-build/application-sdk/report.json'),gpiote_object_sha256=sha(gpiote_object),
        layout_probe_sha256=sha(probe),layout_assertions=6,remaining_symbols=remaining,application_linked=False)
    (out/'integration-report.json').write_text(json.dumps(integration,indent=2)+'\n')
    (out/'report.json').write_text(json.dumps(dict(units=[row],headers=headers,inputs=inputs,application_linked=False,remaining_symbols=undefined,limitations=['Event-open and IRQ dispatch now compile; actual nrfx providers remain explicit link dependencies.','Real nrfx event disable/uninit and registry/GPIO providers are required; no success stubs are linked.']),indent=2)+'\n');print('Named GPIO records and six native bodies compiled; remaining:',', '.join(undefined))
if __name__=='__main__':main()
