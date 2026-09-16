#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link source flash OTP region accessors helpers at authenticated stock entries."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('flash_otp_get_region',0x3fc28,20),('flash_otp_set_region',0x3fc3c,40),('flash_otp_get_current_region',0x3fc64,24),('flash_otp_get_region_size',0x3fc7c,20)]


def build():
    out=ROOT/'build/gx8002-backup-otp-region';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_otp_region.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'otp-region.o')],check=True)
    descriptor=ROOT/'components/shared/gx8002/runtime_gx8002_flash_otp_descriptor.c'
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(descriptor),'-o',str(out/'otp-descriptor.o')],check=True)
    script=out/'otp-region.ld'
    script.write_text('open_cfw_gx8002_flash_state = 0x20016d60;\nSECTIONS {\n'+''.join(f'.text.{name} {offset-0x38940+0x10000000:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'.otp_descriptor 0x20016f4c : { *(.data.open_cfw_gx8002_flash_otp_descriptor) }\n}\n')
    linked=out/'otp-region.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'otp-region.o'),str(out/'otp-descriptor.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved discovery symbol')
    section=next(s for s in e.sections if s['name']=='.otp_descriptor')
    assert section['address']==0x20016f4c and section['size']==20 and not e.relocations(section['index'])
    assert e.contents(section)==stock[0x4f88c:0x4f8a0]
    assert len([s for s in e.sections if s['flags']&2 and s['size']])==5
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if e.relocations(sec['index']):raise ValueError('unresolved discovery relocation')
        payload=e.contents(sec)
        assert len(payload)<=size and sec['address']==offset-0x38940+0x10000000
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size],'fits':len(payload)<=size})
    (out/'otp-region-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'descriptor_source_sha256':sha(descriptor.read_bytes()),'descriptor_bytes':20,'state_header_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_flash_state.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,
            'limits':['Decoded descriptor reads, output writes and region selection require qualification.',
                      'Source descriptor and state require startup linkage; device records and physical hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-otp-region-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
