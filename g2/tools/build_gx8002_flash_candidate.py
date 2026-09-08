#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build reconstructed SPI-NOR initializer without claiming service closure."""
import json
import re
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from link_gx8002_uart_console import ROOT


def build():
    out=ROOT/'build/gx8002-board';out.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    source=ROOT/'components/shared/gx8002/runtime_gx8002_flash_initialize.c'
    flags=['-Os',*FLAGS[1:]]
    subprocess.run([str(prefix)+'gcc',*flags,'-c',str(source),'-o',str(out/'flash.o')],check=True)
    bindings={name:int(address,16) for name,address in re.findall(r'(open_cfw_gx8002_(?:service|callback)_([0-9a-f]{8}))',source.read_text())}
    bindings.update(open_cfw_gx8002_platform_gate=0x10025080,open_cfw_gx8002_flash_state=0x200264e4,open_cfw_gx8002_flash_interface=0x20026504)
    bindings.update(open_cfw_gx8002_platform_config=0x10025d74,open_cfw_gx8002_spi_wait_idle=0x1002364c,open_cfw_gx8002_flash_wait_ready=0x1002375c,open_cfw_gx8002_flash_quad_enable=0x100242b4,open_cfw_gx8002_flash_quad_enable_pair=0x10024330,open_cfw_gx8002_flash_device_config=0x100242ec,open_cfw_gx8002_flash_xip_config=0x1002436c)
    bindings.update(open_cfw_gx8002_flash_discover=0x10024190,open_cfw_gx8002_flash_word_program=0x10023788,open_cfw_gx8002_flash_word_read=0x10023cac)
    script=out/'flash.ld';script.write_text('SECTIONS { .text 0x100245f0 : { *(.text.open_cfw_gx8002_flash_initialize) } .rodata.flash_configuration 0x100246c0 : { *(.rodata.configuration.0) } }\n'+''.join(f'{name} = {value:#x};\n' for name,value in sorted(bindings.items())))
    linked=out/'flash.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(out/'flash.o'),'-o',str(linked)],check=True)
    e=Elf32(linked.read_bytes(),str(linked));s=next(s for s in e.sections if s['name']=='.text')
    if e.relocations(s['index']) or any(x['name'] and x['section']==0 for x in e.symbols()):raise ValueError('unresolved initializer')
    constant=next(x for x in e.sections if x['name']=='.rodata.flash_configuration')
    if s['size']!=208 or constant['address']!=0x100246c0 or e.contents(constant)!=bytes(4) or e.relocations(constant['index']):raise ValueError('configuration constant layout')
    b=IMAGE.read_bytes()
    if sha(b)!=IMAGE_SHA:raise ValueError('stock changed')
    (out/'flash.disassembly.txt').write_text(subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True))
    report={'interface_header_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_flash_interface_table.h').read_bytes()),'state_header_sha256':sha((ROOT/'components/shared/gx8002/runtime_gx8002_flash_state.h').read_bytes()),'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':s['size'],'compiled_sha256':sha(e.contents(s)),
            'package_offset':0x16604,'stock_envelope_bytes':212,'stock_sha256':sha(b[0x16604:0x166d8]),'fits':s['size']<=212,
            'configuration_constant':{'section':constant['name'],'runtime_address':constant['address'],'package_offset':0x166d4,'bytes':4,'sha256':sha(e.contents(constant)),'stock_sha256':sha(b[0x166d4:0x166d8])},'bindings':bindings,'source_admitted':False,'limits':['Decoded path, argument, MMIO and state-write comparison remains required.',
            'All service/callback functions have separate source reconstructions; flash state/interface ownership remains pending.',
            'Complete startup composition, stack capacity and physical flash behavior remain unqualified.']}
    (ROOT/'docs/research/gx8002-flash-initialize-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report['compiled_bytes']);return report

if __name__=='__main__':build()
