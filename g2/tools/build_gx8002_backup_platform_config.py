#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link source platform register configuration helpers at authenticated stock entries."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('platform_config',0x4e08c,228)]


def build():
    out=ROOT/'build/gx8002-backup-platform-config';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_platform_config.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'config.o')],check=True)
    script=out/'config.ld'
    script.write_text('SECTIONS {\n'+''.join(f'.text.{name} {offset-0x3b940+0x10003000:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'.rodata.platform_config 0x10012a3c : { *(.rodata.open_cfw_gx8002_platform_config) }\n}\n')
    linked=out/'config.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'config.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved configuration symbol')
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if e.relocations(sec['index']):raise ValueError('unresolved configuration relocations')
        payload=e.contents(sec)
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size],'fits':len(payload)<=size})
    (out/'config-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    table=next(s for s in e.sections if s['name']=='.rodata.platform_config')
    if table['size']!=40 or e.relocations(table['index']):raise ValueError('invalid generated dispatch table')
    data={'section':table['name'],'compiled_bytes':40,'compiled_sha256':sha(e.contents(table)),
          'package_offset':0x4b37c,'stock_envelope_bytes':40,'stock_sha256':sha(stock[0x4b37c:0x4b3a4])}
    report={'generated_dispatch_table':data,'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,
            'limits':['Placement and decoded dispatcher/input/MMIO qualification required.',
                      'No physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-platform-config-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
