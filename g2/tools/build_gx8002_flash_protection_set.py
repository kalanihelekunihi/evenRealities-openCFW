#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link source flash protection query helpers at authenticated stock entries."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('flash_write_protect_set',0x159b8,204),('flash_write_protect_lock',0x15a84,16),('flash_write_protect_unlock',0x15a94,16)]


def build():
    out=ROOT/'build/gx8002-board';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_protection_set.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'protection-set.o')],check=True)
    script=out/'protection-set.ld'
    script.write_text('open_cfw_gx8002_flash_state = 0x200264e4;\nopen_cfw_gx8002_flash_wait_ready = 0x1002375c;\nopen_cfw_gx8002_flash_read_status = 0x10023734;\nopen_cfw_gx8002_flash_read_status2 = 0x10023770;\nopen_cfw_gx8002_flash_write_enable = 0x1002374c;\nopen_cfw_gx8002_flash_command_write = 0x100236dc;\nopen_cfw_gx8002_flash_write_protect_status = 0x100238ec;\nSECTIONS {\n'+''.join(f'.text.{name} {offset+0x1000dfec:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'}\n')
    linked=out/'protection-set.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'protection-set.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved discovery symbol')
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if e.relocations(sec['index']):raise ValueError('unresolved discovery relocation')
        payload=e.contents(sec)
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size],'fits':len(payload)<=size})
    (out/'protection-set-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'state_header_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_flash_state.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,'analysis_only_overlapping_sections_allowed':False,
            'limits':['Decoded profile reads, status calls and output writes require qualification.',
                      'Protection profile initialization and device table remain retained dependencies; no physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-flash-protection-set-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
