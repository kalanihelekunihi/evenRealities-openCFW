#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Authenticate and rebuild the exact console libc port at its stock entry."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def verify(prefix=None,sdk=None,output=None):
    prefix=prefix or ROOT/'build/csky-macos/install/bin'
    output=output or ROOT/'build/gx8002-fputc'
    output.mkdir(parents=True,exist_ok=True)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_fputc.c'
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    script=output/'fputc.ld'
    script.write_text('SECTIONS { .text.open_cfw_gx8002_fputc 0x10206c70 : { *(.text.open_cfw_gx8002_fputc) } open_cfw_gx8002_console_putc = 0x102037f0; /DISCARD/ : { *(.comment) *(.note*) } }\n')
    obj=output/'fputc.o';linked=output/'fputc.elf'
    subprocess.run([str(prefix/'csky-unknown-elf-gcc'),*FLAGS,'-c',str(source),'-o',str(obj)],check=True)
    subprocess.run([str(prefix/'csky-unknown-elf-ld'),'-T',str(script),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));section=next(s for s in elf.sections if s['name']=='.text.open_cfw_gx8002_fputc')
    payload=elf.contents(section)
    if payload!=stock[0x101fc:0x10206] or elf.relocations(section['index']):raise ValueError('console port differs from stock')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved port symbol')
    return {'symbol':'open_cfw_gx8002_fputc','source_sha256':sha(source.read_bytes()),'compile_flags':FLAGS,
            'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'stock_occurrences':[{
                'symbol':'open_cfw_gx8002_fputc','package_offset':0x101fc,'bytes':10,
                'sha256':sha(payload),'region':'image_a_xip_text'}],
            'source_admitted':True,'hardware_qualified':False,
            'limits':['Experimental hybrid; calls the separately qualified source console entry.']}

if __name__=='__main__':print(json.dumps(verify(),indent=2))
