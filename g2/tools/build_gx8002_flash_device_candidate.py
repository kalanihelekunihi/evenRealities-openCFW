#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build reconstructed device-specific flash configuration without claiming service closure."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT


def build():
    out=ROOT/'build/gx8002-board';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_device_config.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'device.o')],check=True)
    bindings={'open_cfw_gx8002_flash_command_read':0x10023684,
              'open_cfw_gx8002_flash_command_write':0x100236dc,
              'open_cfw_gx8002_flash_wait_ready':0x1002375c,
              'open_cfw_gx8002_flash_write_enable':0x1002374c}
    script=out/'device.ld';script.write_text('SECTIONS { .text 0x100242ec : { *(.text.open_cfw_gx8002_flash_device_config) } }\n'+''.join(f'{name} = {value:#x};\n' for name,value in sorted(bindings.items())))
    linked=out/'device.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'device.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));s=next(s for s in e.sections if s['name']=='.text')
    if e.relocations(s['index']) or any(x['name'] and x['section']==0 for x in e.symbols()):raise ValueError('unresolved initializer')
    b=IMAGE.read_bytes()
    if sha(b)!=IMAGE_SHA:raise ValueError('stock changed')
    (out/'device.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':s['size'],'compiled_sha256':sha(e.contents(s)),
            'package_offset':0x16300,'stock_envelope_bytes':68,'stock_sha256':sha(b[0x16300:0x16344]),'fits':s['size']<=68,
            'bindings':bindings,'source_admitted':False,'limits':['Decoded path, argument, MMIO and state-write comparison remains required.',
            'Command transport and control helpers are separately qualified source dependencies.',
            'Polling has no timeout; physical flash effects remain unqualified.']}
    (ROOT/'docs/research/gx8002-flash-device-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['compiled_bytes']);return report

if __name__=='__main__':build()
