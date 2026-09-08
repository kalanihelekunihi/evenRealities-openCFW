#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rebuild watchdog candidates at original entries, without source admission."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def link():
    output=ROOT/'build/gx8002-app-tick';output.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_watchdog_initialize.c'
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    flags=['-Os',*FLAGS[1:],'-fno-shrink-wrap'];obj=output/'watchdog-initialize.o'
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(obj)],check=True)
    script=output/'watchdog-initialize.ld'
    script.write_text('''SECTIONS {
.text.open_cfw_gx8002_watchdog_interrupt 0x10206704 : { *(.text.open_cfw_gx8002_watchdog_interrupt) }
.text.open_cfw_gx8002_watchdog_initialize 0x10206720 : { *(.text.open_cfw_gx8002_watchdog_initialize) }
.rodata.watchdog_error 0x1020ad1a : SUBALIGN(1) { *(.rodata.open_cfw_gx8002_watchdog_initialize.str1.1) }
}
open_cfw_gx8002_watchdog_handler = 0x20027b48;
open_cfw_gx8002_platform_gate = 0x10025080;
open_cfw_gx8002_request_irq = 0x1002553c;
open_cfw_gx8002_printf = 0x10206c24;
''')
    linked=output/'watchdog-initialize.elf'
    subprocess.run([str(prefix)+'ld','-T',str(script),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));rows=[]
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved watchdog symbol')
    for name,offset,size in [('.text.open_cfw_gx8002_watchdog_interrupt',0xfc90,28),('.text.open_cfw_gx8002_watchdog_initialize',0xfcac,128),('.rodata.watchdog_error',0x142a6,22)]:
        section=next(s for s in elf.sections if s['name']==name);payload=elf.contents(section)
        if len(payload)>size or section['address']!=offset+0x101f6a74 or elf.relocations(section['index']):raise ValueError('watchdog placement failure')
        rows.append({'section':name,'package_offset':offset,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size]})
    report={'source_sha256':sha(source.read_bytes()),'flags':flags,'sections':rows,'source_admitted':False,
            'limits':['Clock-gate and IRQ registration resolve to retained functions, not source closure.',
                      'Target MMIO/callback comparison pending; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-watchdog-initialize-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(link(),indent=2))
