#!/usr/bin/env python3
"""Build authenticated Bosch/ST sensor APIs directly from their pinned trees."""
import hashlib
import json
from pathlib import Path
import subprocess
from audit_source_frontier import functions
from build_source_candidates import undefined_symbols

ROOT=Path(__file__).resolve().parents[2]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest=json.loads((ROOT/'third-party/fetched/manifest.json').read_text())
    by_id={x['id']:x for x in manifest['components']}
    specs=[('bosch-bma456-sensorapi','bosch-bma456','',
            {'bma4.c':'core_source_sha256','bma4.h':'core_header_sha256','bma4_defs.h':'defs_header_sha256',
             'bma456w.c':'variant_source_sha256','bma456w.h':'variant_header_sha256','LICENSE':'license_sha256'}),
           ('st-lis2dw12-pid','st-lis2dw12','',{'lis2dw12_reg.c':'source_sha256','lis2dw12_reg.h':'header_sha256','LICENSE':'license_sha256'}),
           ('st-st25dvxxkc-bsp','st-fp-sns-stbox1','Drivers/BSP/Components/st25dvxxkc',
            {'st25dvxxkc.c':'source_sha256','st25dvxxkc.h':'header_sha256','st25dvxxkc_reg.c':'register_source_sha256',
             'st25dvxxkc_reg.h':'register_header_sha256','LICENSE.md':'license_sha256'})]
    output=ROOT/'r1/research/source-build/sensors';output.mkdir(parents=True,exist_ok=True);(output/'report.json').unlink(missing_ok=True)
    rows=[];dependencies=[]
    flags=['--target=arm-none-eabi','-mcpu=cortex-m4','-mthumb','-mfpu=fpv4-sp-d16','-mfloat-abi=hard',
           '-std=c11','-ffreestanding','-fno-builtin','-fno-strict-aliasing','-fshort-enums','-Os',
           '-ffunction-sections','-fdata-sections','-Wall','-Wextra','-Werror',
           '-isystem',str(ROOT/'vendor-cache/r1/gcc-arm-none-eabi-9-2020-q2-update/arm-none-eabi/include')]
    for component,name,subpath,files in specs:
        pin=by_id[component];tree=ROOT/'third-party/upstream'/name;base=tree/subpath
        assert (tree/'.git').exists()
        observed_head=subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip()
        materialized=False
        if observed_head!=pin['commit']:
            # Preserve another task's checkout. Consume only explicitly named
            # files from the pinned Git objects, then authenticate each digest.
            base=ROOT/'vendor-cache/r1'/f'{name}-{pin["commit"]}'
            base.mkdir(parents=True,exist_ok=True)
            for filename in files:
                relative=str(Path(subpath)/filename) if subpath else filename
                data=subprocess.check_output(['git','-C',str(tree),'show',pin['commit']+':'+relative])
                (base/filename).write_bytes(data)
            materialized=True
        else:
            assert not subprocess.check_output(['git','-C',str(tree),'status','--porcelain'],text=True).strip()
        inputs={}
        for filename,key in files.items():
            assert sha(base/filename)==pin[key],filename
            inputs[str((base/filename).relative_to(ROOT))]=pin[key]
        dependencies.append(dict(component=component,pin=pin['commit'],observed_checkout_head=observed_head,materialized_from_pinned_git_objects=materialized,inputs=inputs,
                                 exact_original_checkout_proven=pin.get('exact_vendor_checkout_proven',component=='bosch-bma456-sensorapi')))
        for filename in files:
            if not filename.endswith('.c'):continue
            source=base/filename;obj=output/f'{name}-{source.stem}.o';obj.unlink(missing_ok=True)
            command=['clang',*flags,'-I'+str(base),'-c',str(source),'-o',str(obj)]
            result=subprocess.run(command,capture_output=True,text=True)
            row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=result.returncode==0,diagnostics=result.stderr)
            if row['compiled']:
                undefined,defined=undefined_symbols(obj);symbols=functions(obj)
                row.update(object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(symbols))
            rows.append(row)
    # Stock's Bosch version discriminator includes these exact callback offsets.
    probe=output/'bma-layout-probe.c'
    probe.write_text('#include <stddef.h>\n#include "bma4.h"\n'+''.join(
        f'_Static_assert(offsetof(struct bma4_dev,{field})=={offset},"stock {field} offset");\n'
        for field,offset in [('bus_read',0x24),('bus_write',0x28),('delay_us',0x2c)]))
    bma_row=next(row for row in rows if row['source'].endswith('/bma4.c'))
    probe_command=list(bma_row['command']);probe_command[probe_command.index('-c')+1]=str(probe);probe_command[-1]=str(output/'bma-layout-probe.o')
    subprocess.run(probe_command,check=True)
    source=ROOT/'r1/components/st25/stock_bus_bindings.c'
    obj=output/'r1-st25-stock-bus.o';obj.unlink(missing_ok=True)
    st25=ROOT/'third-party/upstream/st-fp-sns-stbox1/Drivers/BSP/Components/st25dvxxkc'
    command=['clang',*flags,'-I'+str(st25),'-c',str(source),'-o',str(obj)]
    result=subprocess.run(command,capture_output=True,text=True)
    row=dict(source=str(source.relative_to(ROOT)),source_sha256=sha(source),command=command,compiled=result.returncode==0,diagnostics=result.stderr)
    if row['compiled']:
        undefined,defined=undefined_symbols(obj);symbols=functions(obj)
        row.update(object_sha256=sha(obj),undefined=undefined,defined=defined,emitted_function_count=len(symbols))
    rows.append(row)
    definitions={s for row in rows for s in row.get('defined',[])}
    report=dict(schema=1,r1_binding_header_sha256=sha(ROOT/'r1/components/st25/stock_bus_bindings.h'),bma_callback_offsets={'bus_read':36,'bus_write':40,'delay_us':44},bma_layout_probe_sha256=sha(probe),dependencies=dependencies,units=rows,compiled=sum(row['compiled'] for row in rows),total=len(rows),
                compiler_version=subprocess.check_output(['clang','--version'],text=True),
                unresolved=sorted({s for row in rows for s in row.get('undefined',[])}-definitions),
                image_linked=False,stock_configuration_proven=False,byte_identity_proven=False,
                limitations=['The full public APIs compile, including functions not retained in stock. Symbol counts are candidates only.',
                             'Device objects, R1 bus callbacks, selector policy and hardware behavior require separate implementation and verification.',
                             'LIS2DW12 and ST25DVxxKC pins are compatible snapshots; their original R1 checkout is not uniquely proven.'])
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Sensor/provider units compiled: {report['compiled']}/{report['total']}")
    for row in rows:
        if not row['compiled']:print(row['source']+'\n'+row['diagnostics'][:2500])
    print('External symbols:',', '.join(report['unresolved']))
    return 0 if all(row['compiled'] for row in rows) else 1


if __name__=='__main__':raise SystemExit(main())
