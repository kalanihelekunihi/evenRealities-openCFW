#!/usr/bin/env python3
"""Compile shared R1 i2c_5 transport with actual ST25 and registry components."""
import hashlib
import json
from pathlib import Path
import subprocess
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output=ROOT/'r1/research/source-build/i2c5';output.mkdir(parents=True,exist_ok=True);(output/'report.json').unlink(missing_ok=True)
    source=ROOT/'r1/components/i2c5/stock_transport.c';obj=output/'stock_transport.o';obj.unlink(missing_ok=True)
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
           '-std=c11','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-Os','-ffunction-sections','-fdata-sections',
           '-Wall','-Wextra','-Werror','-fno-delete-null-pointer-checks','-I'+str(ROOT/'r1/reconstructed')]
    command=['clang',*flags,'-c',str(source),'-o',str(obj)];subprocess.run(command,check=True)
    undefined,defined=undefined_symbols(obj)
    rows=[dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=True,
               object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(functions(obj)))]
    registry_source=ROOT/'r1/reconstructed/generic_device_registry/generic_device_registry.c'
    registry_object=output/'generic_device_registry.o'
    registry_command=['clang',*flags,'-c',str(registry_source),'-o',str(registry_object)]
    subprocess.run(registry_command,check=True)
    undefined_registry,defined_registry=undefined_symbols(registry_object)
    rows.append(dict(source=str(registry_source.relative_to(ROOT)),source_sha256=sha(registry_source),command=registry_command,compiled=True,
                     object_sha256=sha(registry_object),undefined=undefined_registry,defined=defined_registry,
                     emitted_function_count=len(functions(registry_object))))
    native_source=ROOT/'r1/components/registry/stock_registry.c'
    native_object=output/'stock_registry.o'
    native_command=['clang',*flags,'-c',str(native_source),'-o',str(native_object)]
    subprocess.run(native_command,check=True)
    native_undefined,native_defined=undefined_symbols(native_object)
    rows.append(dict(source=str(native_source.relative_to(ROOT)),source_sha256=sha(native_source),command=native_command,compiled=True,
                     object_sha256=sha(native_object),undefined=native_undefined,defined=native_defined,
                     emitted_function_count=len(functions(native_object))))
    records_source=ROOT/'r1/components/software-twi/stock_records.c'
    records_object=output/'stock_twi_records.o'
    records_command=['clang',*flags,'-c',str(records_source),'-o',str(records_object)]
    subprocess.run(records_command,check=True)
    records_undefined,records_defined=undefined_symbols(records_object)
    rows.append(dict(source=str(records_source.relative_to(ROOT)),source_sha256=sha(records_source),command=records_command,compiled=True,
                     object_sha256=sha(records_object),undefined=records_undefined,defined=records_defined,
                     emitted_function_count=len(functions(records_object))))
    # Use the real compiled registry and sensor objects; no fake providers.
    sensor_report=json.loads((ROOT/'r1/research/source-build/sensors/report.json').read_text())
    provider_report=json.loads((ROOT/'r1/research/source-build/report.json').read_text())
    needed=['r1/components/st25/stock_bus_bindings.c',
            'st25dvxxkc/st25dvxxkc.c','st25dvxxkc/st25dvxxkc_reg.c']
    inputs=[obj,registry_object,native_object,records_object];dependencies=[]
    for name in needed:
        row=next(row for report in (sensor_report,provider_report) for row in report['units'] if Path(row['source']).as_posix().endswith(name))
        p=Path(row['command'][-1]);assert row['compiled'] and sha(p)==row['object_sha256']
        assert sha(ROOT/row['source'])==row['source_sha256']
        inputs.append(p);dependencies.append(dict(source=row['source'],object=str(p.relative_to(ROOT)),object_sha256=sha(p)))
    gpio_report=json.loads((ROOT/'r1/research/source-build/software-twi/gpio-report.json').read_text())
    for path,digest in gpio_report['inputs'].items():assert sha(ROOT/path)==digest,path
    gpio=gpio_report['units'][0];gpio_object=Path(gpio['command'][-1]);assert sha(gpio_object)==gpio['object_sha256']
    inputs.append(gpio_object);dependencies.append(dict(source=gpio['source'],object=str(gpio_object.relative_to(ROOT)),object_sha256=sha(gpio_object)))
    twi_source=ROOT/'r1/reconstructed/software_twi/software_twi.c'
    twi_object=output/'software_twi.o'
    twi_command=['clang',*flags,'-DSOFTWARE_TWI_NATIVE_CONTRACT=1','-c',str(twi_source),'-o',str(twi_object)]
    subprocess.run(twi_command,check=True)
    twi_undefined,twi_defined=undefined_symbols(twi_object)
    rows.append(dict(source=str(twi_source.relative_to(ROOT)),source_sha256=sha(twi_source),command=twi_command,compiled=True,
                     object_sha256=sha(twi_object),undefined=twi_undefined,defined=twi_defined,
                     emitted_function_count=len(functions(twi_object))))
    inputs.append(twi_object)
    relocatable=output/'st25-i2c5-registry.o'
    subprocess.run(['arm-none-eabi-ld','-r',*map(str,inputs),'-o',str(relocatable)],check=True)
    remaining,_=undefined_symbols(relocatable)
    report=dict(schema=1,units=rows,
                headers={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'r1/components/software-twi/stock_records.h',ROOT/'r1/reconstructed/software_twi/software_twi.h',ROOT/'r1/components/i2c5/stock_transport.h',ROOT/'r1/components/registry/stock_registry.h',ROOT/'r1/components/st25/stock_bus_bindings.h',ROOT/'r1/reconstructed/generic_device_registry/generic_device_registry.h']},
                dependencies=dependencies,relocatable_link=True,relocatable_sha256=sha(relocatable),remaining_external_symbols=remaining,
                compiler_version=subprocess.check_output(['clang','--version'],text=True),application_linked=False,instruction_identity=False,
                native_engine_contract=True,null_pointer_accesses_preserved=True,limitations=['The relocatable link retains genuine upstream ST25 API and millisecond-delay requirements.',
                             'Transport uses native registry dispatchers, preserving stock NULL-table dereference and operation argument contracts; the older contextual registry remains available for other consumers.',
                             'Native TWI records are source initialized; GPO/ADC and other board record population remains open.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('i2c_5 source compiled and linked with real ST25 board bindings and registry; remaining:',', '.join(remaining))


if __name__=='__main__':main()
