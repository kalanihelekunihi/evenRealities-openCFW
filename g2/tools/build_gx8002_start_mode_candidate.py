#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Native macOS build of reconstructed reset-reason and start-mode queries."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT
from verify_gx8002_analog_source import FLAGS


def build():
    out=ROOT/'build/gx8002-start-mode';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_start_mode.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'mode.o')],check=True)
    script=out/'mode.ld'
    script.write_text('SECTIONS { .reason 0x10024940 : { *(.text.open_cfw_gx8002_reset_reason) } .mode 0x10024984 : { *(.text.open_cfw_gx8002_start_mode) } }\n')
    linked=out/'mode.elf'
    subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'mode.o'),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved query')
    rows=[]
    for name,symbol,offset,size in [('.reason','open_cfw_gx8002_reset_reason',0x16954,68),('.mode','open_cfw_gx8002_start_mode',0x16998,32)]:
        section=next(s for s in elf.sections if s['name']==name)
        if section['size']>size or elf.relocations(section['index']):raise ValueError('query placement failed')
        rows.append({'section':name,'symbol':symbol,'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),
                     'package_offset':offset,'stock_envelope_bytes':size,'stock_sha256':sha(stock[offset:offset+size])})
    (out/'mode.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':rows,'source_admitted':False,
            'limits':['Decoded MMIO/return-value comparison remains required.', 'Register meanings and hardware read side effects are not inferred.']}
    (ROOT/'docs/research/gx8002-start-mode-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return report

if __name__=='__main__':build()
