#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Resolve the complete SDK DW SPI object as a comparison oracle only."""
import json
import subprocess
from analyze_gx8002_upstream_objects import ROOT, SDK_COMMIT, authenticated_blob, IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32


def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    rel='drivers_lib/spi/dw_spi/spi_master_v3.o'
    blob='600d763a219007e2af7b5006989d44984abf0861'
    data=authenticated_blob(sdk/rel,blob)
    sections=(('dw_spi_cleanup',0xf6f0,12),('spi_master_irq_handler',0xf6fc,32),
              ('dw_spi_setup',0xf71c,116),('dw_spi_quick_transfer',0xf790,634),
              ('spi_master_v3_probe',0xfa0c,268))
    out=ROOT/'build/gx8002-board'
    script=out/'dw-spi-full-oracle.ld'
    script.write_text('SECTIONS {\n'+''.join(
        f'.text.{name} {offset+0x101f6a74:#x} : {{ KEEP(*(.text.{name})) }}\n'
        for name,offset,size in sections)+'.bss 0x20027ae0 : { *(.bss) }\n}\n'
        'gx_clock_set_module_enable = 0x10025080;\n'
        'gx_clock_get_module_frequence = 0x10025210;\n'
        'spi_register_master = 0x102060fc;\n'
        'gx_request_irq = 0x1002553c;\n')
    target=out/'dw-spi-full-oracle.elf'
    subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-ld'),
                    '--gc-sections','-T',str(script),str(sdk/rel),'-o',str(target)],check=True)
    linked=Elf32(target.read_bytes(),str(target))
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:
        raise ValueError('Stock identity')
    matches=[]
    for name,offset,size in sections:
        sec=next(s for s in linked.sections if s['name']=='.text.'+name)
        payload=linked.contents(sec)
        if payload!=stock[offset:offset+size]:
            raise ValueError('Full SPI section mismatch '+name)
        matches.append({'symbol':name,'package_offset':offset,'bytes':size,'sha256':sha(payload)})
    return {'sdk_commit':SDK_COMMIT,'object':rel,'blob':blob,'object_sha256':sha(data),
            'full_relocated_matches':matches,
            'bss_symbols':{'spi_device_context_tab':0x20027ae0,'dw_spi_master':0x20027af0,'dwspi':0x20027b14},
            'source_admitted':False,
            'limits':['All SDK object bytes remain comparison-only. Private-state meanings require instruction-level recovery; no hardware proof.']}

if __name__=='__main__':
    report=analyze()
    (ROOT/'docs/research/gx8002-dw-spi-probe-attribution.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Matched',len(report['full_relocated_matches']),'complete sections')
