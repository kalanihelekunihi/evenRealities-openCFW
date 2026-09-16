# SPDX-License-Identifier: MIT
"""Inventory stock system initialization calls against current source allocations."""
import json, subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def analyze():
    stock=IMAGE.read_bytes(); assert sha(stock)==IMAGE_SHA
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    source=subprocess.check_output(['git','-C',str(sdk),'show',SDK_COMMIT+':lvp/common/lvp_system_init.c'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    code=decode(subprocess.check_output([pre,'-D','--start-address=0x4322c','--stop-address=0x43398',str(wrapper)],text=True))
    cluster_path=ROOT/'build/gx8002-backup-startup-cluster/cluster.elf'
    cluster=Elf32(cluster_path.read_bytes(),'source')
    symbols=cluster.symbols()
    names={0x3dae4:'gx_cache_init',0x3d654:'gx_dma_init',0x3d148:'gx_console_init',0x3c8f8:'gx_pmu_get_wakeup_source',0x3d93c:'gx_timer_init',0x3d16c:'gx_irq_init',0x40b44:'device_list_init',0x40eec:'spi_master_v3_probe',0x43084:'LvpPmuInit',0x42274:'printf',0x408ec:'gx_spi_flash_probe',0x4094c:'gx_spi_flash_gettype',0x40958:'gx_spi_flash_getinfo',0x40a74:'gx_analog_get_ldo_dig_ctrl',0x40b2c:'gx_gpio_init',0x412b8:'BoardInit',0x4115c:'gx_rtc_init',0x41150:'gx_rtc_set_tick',0x41140:'gx_rtc_start_tick',0x3c630:'clock frequency helper',0x3c81c:'analog trim getter'}
    calls={}
    for pc,(op,args,width) in sorted(code.items()):
        if op=='bsr': calls.setdefault(int(args,0),[]).append(pc)
    rows=[]
    for target,sites in calls.items():
        address=target+0x10000000-0x38940
        allocated=[s['name'] for s in symbols if s['value']==address and s['section'] not in (0,0xfff1) and s['name']]
        rows.append({'package_target':hex(target),'runtime_target':hex(address),'inferred_sdk_name':names.get(target),'call_sites':[hex(x) for x in sites],'allocated_source_symbols':allocated})
    report={'stock_sha256':IMAGE_SHA,'sdk_commit':SDK_COMMIT,'sdk_source_sha256':sha(source),'cluster_sha256':sha(cluster_path.read_bytes()),'calls':rows,'source_target_count':sum(bool(row['allocated_source_symbols']) for row in rows),'target_count':len(rows),'limits':['Names are inferred from upstream call ordering and recovered arguments, not symbol-table evidence; unnamed targets need further review.', 'Allocated symbols demonstrate current source linkage only, not behavior or hardware qualification. Initializer and cold-start diagnostics now have a separate source candidate and modeled verification; this dependency census does not establish composed execution.']}
    (ROOT/'docs/research/gx8002-backup-system-dependencies.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__=='__main__': print(json.dumps(analyze(),indent=2))
