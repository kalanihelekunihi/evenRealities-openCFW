#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Link recovered UART dispatcher and source-authored diagnostic string."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def link():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';output=ROOT/'build/gx8002-uart-tick';output.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    records=[]
    for relative in ('lvp/common/uart_message_v2.h','lvp/common/lvp_queue.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',f'{SDK_COMMIT}:{relative}'],text=True).strip()
        records.append({'path':relative,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/relative,blob))})
    source=ROOT/'components/shared/gx8002/runtime_gx8002_uart_async_tick.c'
    obj=output/'tick.o';linked=output/'tick.elf';script=output/'tick.ld'
    script.write_text('''SECTIONS {
.text.open_cfw_gx8002_uart_async_tick 0x10208334 : { *(.text.open_cfw_gx8002_uart_async_tick) }
.rodata.uart_error 0x1020b17d : SUBALIGN(1) { *(.rodata.open_cfw_gx8002_uart_async_tick.str1.4) }
}
LvpQueueGet = 0x10206fb0;
open_cfw_gx8002_crc32 = 0x102098a8;
open_cfw_gx8002_printf = 0x10206c24;
open_cfw_gx8002_uart_receive_queue = 0x2002ecc4;
open_cfw_gx8002_uart_registrations = 0x2002e360;
''')
    subprocess.run([str(prefix)+'gcc',*FLAGS,'-I',str(sdk/'lvp/common'),'-c',str(source),'-o',str(obj)],check=True)
    subprocess.run([str(prefix)+'ld','-T',str(script),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));rows=[]
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved dispatcher dependency')
    for name,offset,size in (('.text.open_cfw_gx8002_uart_async_tick',0x118c0,136),('.rodata.uart_error',0x14709,14)):
        section=next(s for s in elf.sections if s['name']==name);payload=elf.contents(section)
        if section['address']!=offset+0x101f6a74 or len(payload)>size or elf.relocations(section['index']):raise ValueError('dispatcher placement failure')
        if name.startswith('.rodata') and payload!=b'Crc Error %d\n\0':raise ValueError('diagnostic string changed')
        rows.append({'section':name,'package_offset':offset,'compiled_bytes':len(payload),
                     'compiled_sha256':sha(payload),'stock_envelope_bytes':size,
                     'stock_sha256':sha(stock[offset:offset+size]),'byte_exact':payload==stock[offset:offset+size]})
    report={'sdk_commit':SDK_COMMIT,'upstream_files':records,'source_sha256':sha(source.read_bytes()),
            'flags':FLAGS,'sections':rows,'source_admitted':False,
            'limits':['Linked placement only; target callback/CRC/queue path comparison pending.',
                      'Existing queue and registration state remain retained.']}
    (ROOT/'docs/research/gx8002-uart-tick-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(link(),indent=2))
