#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link source flash status and write-enable helpers at authenticated stock entries."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('flash_read_status',0x15748,24),('flash_write_enable',0x15760,16),
      ('flash_wait_ready',0x15770,20),('flash_read_status2',0x15784,24)]


def build():
    out=ROOT/'build/gx8002-board';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_status.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'status.o')],check=True)
    script=out/'status.ld'
    script.write_text('open_cfw_gx8002_flash_command_read = 0x10023684;\nopen_cfw_gx8002_flash_command_write = 0x100236dc;\nSECTIONS {\n'+''.join(f'.text.{name} {offset+0x1000dfec:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'}\n')
    linked=out/'status.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'status.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved status symbol')
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if sec['size']>size or e.relocations(sec['index']):raise ValueError('status placement failure')
        payload=e.contents(sec)
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size]})
    (out/'status-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,
            'limits':['Decoded status helpers require transport-call and stack qualification.',
                      'Polling has no timeout; no physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-flash-status-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
