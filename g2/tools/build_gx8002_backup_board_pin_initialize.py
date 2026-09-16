#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link recovered backup board pin initializer."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

ROWS=[('backup_board_pin_initialize',0x412b8,112)]


def build():
    out=ROOT/'build/gx8002-backup-board-pin-initialize';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_backup_board_pin_initialize.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'erase.o')],check=True)
    script=out/'erase.ld'
    script.write_text('open_cfw_gx8002_padmux_init = 0x10008770;\nopen_cfw_gx8002_padmux_check = 0x100086dc;\nopen_cfw_gx8002_gpio_set_direction = 0x10008154;\nopen_cfw_gx8002_printf = 0x10009934;\nopen_cfw_gx8002_board_pin_setup = 0x100088cc;\nSECTIONS {\n'+''.join(f'.text.{name} {offset-0x38940+0x10000000:#x} : {{ *(.text.open_cfw_gx8002_{name}) }}\n' for name,offset,size in ROWS)+'}\n')
    linked=out/'erase.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'erase.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if any(s['name'] and s['section']==0 for s in e.symbols()):raise ValueError('unresolved erase symbol')
    functions=[]
    for name,offset,size in ROWS:
        sec=next(s for s in e.sections if s['name']=='.text.'+name)
        if e.relocations(sec['index']):raise ValueError('unresolved erase relocation')
        payload=e.contents(sec)
        assert len(payload)<=size and sec['address']==offset-0x38940+0x10000000
        functions.append({'symbol':'open_cfw_gx8002_'+name,'section':sec['name'],'compiled_bytes':len(payload),
                          'compiled_sha256':sha(payload),'package_offset':offset,'stock_envelope_bytes':size,
                          'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size],'fits':len(payload)<=size})
    (out/'erase-linked.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'state_header_sha256':sha((source.parent/'runtime_gx8002_flash_state.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':flags,'functions':functions,'source_admitted':False,'analysis_only_overlapping_sections_allowed':False,
            'limits':['Pin table, diagnostic string, flag and helper implementations require source integration.',
                      'No physical flash qualification.']}
    (ROOT/'docs/research/gx8002-backup-board-pin-initialize-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(f['symbol'],f['compiled_bytes'],f['byte_exact']) for f in functions]);return report

if __name__=='__main__':build()
