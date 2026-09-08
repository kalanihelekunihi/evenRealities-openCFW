#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Rebuild application tick and watchdog ping at recovered target entries."""
import json
import subprocess
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, SDK_COMMIT, authenticated_blob, sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT


def link():
    sdk=ROOT/'build/upstream-nationalchip-lvp-kws';output=ROOT/'build/gx8002-app-tick';output.mkdir(exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock identity changed')
    records=[]
    for relative in ('lvp/app_core/lvp_app.h','lvp/app_core/lvp_app_core.h','lvp/common/lvp_queue.h'):
        blob=subprocess.check_output(['git','-C',str(sdk),'rev-parse',f'{SDK_COMMIT}:{relative}'],text=True).strip()
        records.append({'path':relative,'git_blob':blob,'sha256':sha(authenticated_blob(sdk/relative,blob))})
    rows=[];objects=[];flags=FLAGS+['-fno-shrink-wrap']
    for stem,symbol,offset,size in [('app_tick','LvpAppEventTick',0x122d4,80),('watchdog_ping','open_cfw_gx8002_watchdog_ping',0xfd2c,10)]:
        source=ROOT/f'components/shared/gx8002/runtime_gx8002_{stem}.c';obj=output/f'{stem}.o';objects.append(obj)
        subprocess.run([str(prefix)+'gcc',*flags,'-I',str(sdk/'lvp/app_core'),'-I',str(sdk/'lvp/common'),'-I',str(sdk/'include'),'-c',str(source),'-o',str(obj)],check=True)
        rows.append({'symbol':symbol,'source_sha256':sha(source.read_bytes()),'package_offset':offset,'stock_envelope_bytes':size})
    script=output/'tick.ld'
    script.write_text('SECTIONS {\n'+ '\n'.join(f'.text.{r["symbol"]} 0x{r["package_offset"]+0x101f6a74:x} : {{ *(.text.{r["symbol"]}) }}' for r in rows)+'''
}
LvpQueueGet = 0x10206fb0;
open_cfw_gx8002_app_core_ops = 0x20026d38;
open_cfw_gx8002_app_event_queue = 0x2002ecd8;
open_cfw_gx8002_uart_async_tick = 0x10208334;
''')
    linked=output/'tick.elf'
    subprocess.run([str(prefix)+'ld','-T',str(script),*[str(o) for o in objects],'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked))
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved tick dependency')
    for row in rows:
        section=next(s for s in elf.sections if s['name']=='.text.'+row['symbol']);payload=elf.contents(section)
        if len(payload)>row['stock_envelope_bytes'] or elf.relocations(section['index']):raise ValueError('tick placement failure')
        offset=row['package_offset'];original=stock[offset:offset+row['stock_envelope_bytes']]
        row.update(compiled_bytes=len(payload),compiled_sha256=sha(payload),stock_sha256=sha(original),byte_exact=payload==original)
    report={'sdk_commit':SDK_COMMIT,'upstream_files':records,'flags':flags,'functions':rows,'source_admitted':False,
            'limits':['Event tick target path comparison pending; existing app and queue state retained.','Hardware and timing unqualified.']}
    (ROOT/'docs/research/gx8002-app-tick-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(link(),indent=2))
