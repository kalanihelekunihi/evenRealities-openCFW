#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify source-defined clock tables after resolving their target pointers."""
import json
import subprocess
from build_gx8002_platform_gate_candidate import build
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from link_gx8002_uart_console import ROOT


def verify():
    evidence=build()
    output=ROOT/'build/gx8002-platform-gate'
    script=output/'tables.ld'
    # Only the lookup helper is at its firmware entry; gate code is analysis-only.
    script.write_text('''SECTIONS {
.text.__module_get_info 0x10024a44 : { *(.text.__module_get_info) }
.text 0x11000000 : { *(.text*) }
.rodata : { *(.rodata*) }
.data.gx_clock_param_table 0x200266e0 : { *(.data.gx_clock_param_table) }
.data.gx_clock_dto_table 0x20026880 : { *(.data.gx_clock_dto_table) }
.data.gx_clock_div_table 0x20026884 : { *(.data.gx_clock_div_table) }
}
''')
    linked=output/'tables.elf'
    subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-ld'),'-T',str(script),str(output/'gate.o'),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    rows=[]
    for name,offset,address,size in [('param',0x186f4,0x200266e0,416),('dto',0x18894,0x20026880,3),('div',0x18898,0x20026884,68)]:
        section=next(s for s in elf.sections if s['name']=='.data.gx_clock_'+name+'_table')
        data=elf.contents(section)
        if len(data)!=size or section['address']!=address or elf.relocations(section['index']):raise ValueError('table placement changed')
        if data!=stock[offset:offset+size]:raise ValueError('source clock table differs from stock: '+name)
        rows.append({'symbol':'gx_clock_'+name+'_table','section_name':section['name'],'package_offset':offset,'runtime_address':address,'bytes':size,'sha256':sha(data),'byte_exact':True})
    helper=next(s for s in elf.sections if s['name']=='.text.__module_get_info')
    payload=elf.contents(helper)
    if helper['address']!=0x10024a44 or len(payload)>164 or elf.relocations(helper['index']):
        raise ValueError('module lookup placement failure')
    lookup={'package_offset':0x16a58,'runtime_address':helper['address'],'compiled_bytes':len(payload),
            'compiled_sha256':sha(payload),'stock_envelope_bytes':164,
            'stock_sha256':sha(stock[0x16a58:0x16afc]),'behavior_qualified':False}
    report={'upstream_build':evidence,'tables':rows,'source_table_bytes':sum(r['bytes'] for r in rows),
            'module_lookup':lookup,
            'source_admitted':False,'limits':['Lookup helper fits original entry; gate code remains at a temporary analysis address.',
                                             'One alignment byte between DTO and divider table remains outside table ownership.',
                                             'Clock code qualification and firmware integration remain pending.']}
    (ROOT/'docs/research/gx8002-clock-tables-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

if __name__=='__main__':print(json.dumps(verify(),indent=2))
