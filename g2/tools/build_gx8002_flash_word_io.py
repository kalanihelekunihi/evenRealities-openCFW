#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link source flash word I/O helpers at authenticated stock entries."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('flash_word_read',0x15cc0,172),('flash_word_program',0x1579c,148)]


def build():
    out=ROOT/'build/gx8002-board';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_word_io.c'
    flags=['-Os','-fno-shrink-wrap',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'word-io.o')],check=True)
    script=out/'word-io.ld'
    script.write_text('open_cfw_gx8002_flash_state = 0x200264e4;\nopen_cfw_gx8002_spi_wait_idle = 0x1002364c;\nopen_cfw_gx8002_spi_wait_rx_empty = 0x1002365c;\nopen_cfw_gx8002_spi_wait_tx_empty = 0x10023670;\nopen_cfw_gx8002_flash_wait_ready = 0x1002375c;\nSECTIONS {\n'+''.join(f'.text.{name} {offset+0x1000dfec:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'}\n')
    linked=out/'word-io.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'word-io.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved word I/O symbol')
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if e.relocations(sec['index']):raise ValueError('unresolved word I/O relocation')
        payload=e.contents(sec)
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size],'fits':len(payload)<=size})
    (out/'word-io-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'state_header_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_flash_state.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,
            'limits':['Decoded word transfers and ordered MMIO require qualification.',
                      'Source polling dependencies; state remains retained; no physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-flash-word-io-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
