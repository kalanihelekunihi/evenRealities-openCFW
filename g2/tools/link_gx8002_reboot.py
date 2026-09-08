#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rebuild watchdog reboot and callback at original target addresses."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def link():
    output=ROOT/'build/gx8002-app-tick';output.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_reboot.c'
    flags=['-Os',*FLAGS[1:],'-fno-inline'];obj=output/'reboot.o'
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(obj)],check=True)
    script=output/'reboot.ld';script.write_text('''SECTIONS {
.text.open_cfw_gx8002_reboot 0x102067b8 : { *(.text.open_cfw_gx8002_reboot) }
.text.open_cfw_gx8002_watchdog_callback 0x10208c98 : { *(.text.open_cfw_gx8002_watchdog_callback) }
}
open_cfw_gx8002_platform_gate = 0x10025080;
''')
    linked=output/'reboot.elf'
    subprocess.run([str(prefix)+'ld','-T',str(script),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    rows=[]
    for name,offset,size in [('reboot',0xfd44,36),('watchdog_callback',0x12224,8)]:
        symbol='open_cfw_gx8002_'+name;section=next(s for s in elf.sections if s['name']=='.text.'+symbol);payload=elf.contents(section)
        if len(payload)>size or section['address']!=offset+0x101f6a74 or elf.relocations(section['index']):raise ValueError('reboot placement failure')
        if name=='reboot' and payload!=stock[offset:offset+size]:raise ValueError('reboot body differs from stock')
        rows.append({'symbol':symbol,'package_offset':offset,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size]})
    report={'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':rows,'source_admitted':False,
            'limits':['Clock gate resolves to separately qualified source entry.','Reset wait is stock behavior; no physical reset or hardware qualification.','Callback path comparison pending.']}
    (ROOT/'docs/research/gx8002-reboot-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(link(),indent=2))
