#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile named flash dispatch data; stock is a comparison oracle only."""
import contextlib,io,json,subprocess
from analyze_gx8002_flash_interface import analyze
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_analog_source import FLAGS
from link_gx8002_uart_console import ROOT

def build():
    with contextlib.redirect_stdout(io.StringIO()):inventory=analyze()
    rows=json.loads((ROOT/'docs/research/gx8002-flash-interface-source-bindings.json').read_text())
    if len(rows)!=30:raise ValueError('interface slot count')
    for a,b in zip(rows,inventory['slots']):
        if any(a[k]!=b[k] for k in ('index','name','declaration','runtime_address','package_offset')):
            raise ValueError('upstream interface layout changed')
    out=ROOT/'build/gx8002-board';base=ROOT/'components/shared/gx8002'
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    header=base/'runtime_gx8002_flash_interface_table.h';source=base/'runtime_gx8002_flash_interface_table.c'
    # Every prototype must compile together with the actual implementation.
    source_hashes={}
    for filename in sorted({r['source_file'] for r in rows if r['symbol']}):
        p=base/filename;source_hashes[filename]=sha(p.read_bytes())
        subprocess.run([pre+'gcc',*FLAGS,'-include',str(header),'-fsyntax-only',str(p)],check=True)
    obj=out/'flash-interface-table.o';linked=out/'flash-interface-table.elf'
    subprocess.run([pre+'gcc',*FLAGS,'-c',str(source),'-o',str(obj)],check=True)
    script=out/'flash-interface-table.ld'
    script.write_text('SECTIONS { .data.flash_interface 0x20026504 : { *(.data.open_cfw_gx8002_flash_interface) } }\n'+
                      ''.join(f'{r["symbol"]} = {r["runtime_address"]:#x};\n' for r in rows if r['symbol']))
    subprocess.run([pre+'ld','-T',str(script),str(obj),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));section=next(s for s in elf.sections if s['name']=='.data.flash_interface')
    payload=elf.contents(section);stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    if len(payload)!=120 or section['align']!=4 or elf.relocations(section['index']):raise ValueError('interface layout')
    if any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('undefined callback')
    if payload!=stock[0x18518:0x18590]:raise ValueError('interface contents')
    report={'source_sha256':sha(source.read_bytes()),'header_sha256':sha(header.read_bytes()),
            'implementation_source_sha256':source_hashes,'sdk_commit':inventory['sdk_commit'],
            'sdk_header_git_blob':inventory['header_git_blob'],'flags':FLAGS,'bytes':120,
            'compiled_sha256':sha(payload),'non_null_callbacks':23,'null_slots':7,
            'source_admitted':False,'hardware_qualified':False,
            'limits':['Initializer declarations now use the same struct; admission and whole-codec integration remain.',
                      'Recovered callback types compile with implementations; SDK public API type differences require explicit reconciliation for whole-source integration.']}
    (ROOT/'docs/research/gx8002-flash-interface-table-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2));return report
if __name__=='__main__':build()
