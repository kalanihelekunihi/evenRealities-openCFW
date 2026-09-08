#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build both fitting registry candidates without admitting their behavior."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def link():
    output=ROOT/'build/gx8002-app-tick';output.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_power_registration.c'
    header=source.with_suffix('.h');stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    flags=['-Os',*FLAGS[1:],'-fno-tree-loop-optimize','-fno-guess-branch-probability','-fno-gcse']
    obj=output/'suspend-registration.o'
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(obj)],check=True)
    script=output/'suspend-registration.ld'
    script.write_text('''SECTIONS {
.text.open_cfw_gx8002_register_suspend 0x102076c0 : { *(.text.open_cfw_gx8002_register_suspend) }
.text.open_cfw_gx8002_register_resume 0x10207718 : { *(.text.open_cfw_gx8002_register_resume) }
}
open_cfw_gx8002_power_state = 0x2002dfbc;
open_cfw_gx8002_memcpy = 0x10025738;
''')
    linked=output/'suspend-registration.elf'
    subprocess.run([str(prefix)+'ld','-T',str(script),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked))
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved registration symbol')
    rows=[]
    for name,offset in [('suspend',0x10c4c),('resume',0x10ca4)]:
        symbol='open_cfw_gx8002_register_'+name
        section=next(s for s in elf.sections if s['name']=='.text.'+symbol)
        payload=elf.contents(section)
        if section['address']!=offset+0x101f6a74 or len(payload)>88 or elf.relocations(section['index']):raise ValueError('registration placement failure')
        original=stock[offset:offset+88]
        rows.append({'symbol':symbol,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),
                     'stock_package_offset':offset,'stock_envelope_bytes':88,'stock_sha256':sha(original),
                     'byte_exact':payload==original})
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':sha(header.read_bytes()),'flags':flags,
            'functions':rows,'source_admitted':False,'limits':['Target registry mutation comparison pending.',
            'Existing power state remains retained; hardware timing unqualified.']}
    (ROOT/'docs/research/gx8002-suspend-registration-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(link(),indent=2))
