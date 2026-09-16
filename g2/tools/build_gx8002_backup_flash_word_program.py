#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link reconstructed backup flash word programming."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('flash_word_program',0x3f6d0,212)]


def build():
    out=ROOT/'build/gx8002-backup-flash-word-program';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_flash_word_program.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'transport.o')],check=True)
    script=out/'transport.ld'
    script.write_text('open_cfw_gx8002_flash_wait_ready = 0x10007350;\nSECTIONS {\n'+''.join(f'.text.{name} {offset+0x0ffc76c0:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'}\n')
    linked=out/'transport.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'transport.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved transport symbol')
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if sec['size']>size or e.relocations(sec['index']):raise ValueError('transport placement failure')
        payload=e.contents(sec)
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size]})
    (out/'transport-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,
            'limits':['Readiness schedules, buffer accesses and complete transfer traces require qualification.',
                      'Polling has no timeout; no physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-flash-word-program-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
