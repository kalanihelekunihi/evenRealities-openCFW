#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Relocate RTC SDK sections for attribution only; never a firmware provider."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,SDK_COMMIT,authenticated_blob,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32


def analyze():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';rel='drivers_lib/rtc/dw_rtc.o'
    blob='bc29abc7e65c826c8e5a2cd0799988445b5d50ff';data=authenticated_blob(sdk/rel,blob)
    out=ROOT/'build/gx8002-board';out.mkdir(parents=True,exist_ok=True)
    placements=(('rtc_isr',0xfc0c,0x10206680,32),('gx_rtc_start_tick',0xfc2c,0x102066a0,16),('gx_rtc_set_tick',0xfc3c,0x102066b0,12))
    script=out/'rtc-primitives-oracle.ld'
    script.write_text('SECTIONS {\n'+''.join(f'.text.{name} {address:#x} : {{ KEEP(*(.text.{name})) }}\n' for name,offset,address,size in placements)+'.bss 0x20027b40 : { *(.bss) }\n}\n')
    target=out/'rtc-primitives-oracle.elf'
    subprocess.run([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-ld'),'--gc-sections','-T',str(script),str(sdk/rel),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('RTC stock identity')
    rows=[]
    for name,offset,address,size in placements:
        section=next(s for s in elf.sections if s['name']=='.text.'+name);payload=elf.contents(section)
        if len(payload)!=size or payload!=stock[offset:offset+size]:raise ValueError('RTC relocated section mismatch '+name)
        rows.append({'symbol':name,'package_offset':offset,'runtime_address':address,'bytes':size,'sha256':sha(payload),'full_relocated_section_match':True})
    return {'sdk_commit':SDK_COMMIT,'object':rel,'blob':blob,'object_sha256':sha(data),'sections':rows,
            'bindings':{'.bss':0x20027b40},'source_admitted':False,
            'limits':['Comparison-only authenticated SDK object; none of its bytes are linked into reconstructed firmware.']}

if __name__=='__main__':
    report=analyze();(ROOT/'docs/research/gx8002-rtc-primitives-attribution.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Matched complete relocated RTC sections:',len(report['sections']))
