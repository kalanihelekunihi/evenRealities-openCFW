# SPDX-License-Identifier: MIT
"""Check a proposed table placement in reviewed source-owned envelope fill."""
import json
import subprocess
from link_gx8002_clock_frequency_table_probe import build,ROOT,Elf32,sha
from build_gx8002_platform_config import build as build_host
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA


def analyze():
    evidence=build()
    build_host()
    host=json.loads((ROOT/'docs/research/gx8002-platform-config-verification.json').read_text())['functions'][0]
    occurrence=host['stock_occurrences'][0]
    offset=occurrence['package_offset']+host['compiled_bytes'];size=16
    start=occurrence['package_offset']
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or sha(stock[start:start+occurrence['bytes']])!=occurrence['sha256']:
        raise ValueError('Placement original host identity')
    host_elf=Elf32((ROOT/'build/gx8002-board/config.elf').read_bytes(),'placement host')
    section=next(s for s in host_elf.sections if s['name']==host['section_name'])
    payload=host_elf.contents(section)
    if len(payload)!=host['compiled_bytes'] or sha(payload)!=host['compiled_sha256'] or offset+size!=start+occurrence['bytes']:
        raise ValueError('Placement host envelope')
    address=offset+0x1000dfec
    if address%4:raise ValueError('Placement alignment')
    out=ROOT/'build/gx8002-clock-frequency-table-probe'
    script=(out/'analysis.ld').read_text().replace('0x11001000',hex(address)).replace('0x11000000','0x10025460')
    (out/'placement.ld').write_text(script)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(out/'placement.ld'),str(out/'frequency.o'),'-o',str(out/'placement.elf')],check=True)
    elf=Elf32((out/'placement.elf').read_bytes(),'clock placement')
    rows=[]
    for name in ('.text.open_cfw_gx8002_clock_frequency','.rodata.open_cfw_gx8002_clock_frequency','.rodata.subband_hz'):
        sec=next(s for s in elf.sections if s['name']==name)
        if elf.relocations(sec['index']):raise ValueError('Placement relocation')
        rows.append({'section':name,'address':sec['address'],'bytes':sec['size'],'sha256':sha(elf.contents(sec))})
    (out/'placement.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(out/'placement.elf')],text=True))
    return {'candidate':evidence,'host_symbol':host['symbol'],'host_compiled_sha256':host['compiled_sha256'],'host_stock_sha256':occurrence['sha256'],
            'table_package_offset':offset,'table_runtime_address':address,'sections':rows,'source_admitted':False,
            'limits':['Isolated proposed placement only. Builder overlap/carving support and host/control-flow qualification required; firmware unchanged.']}

if __name__=='__main__':
    result=analyze();(ROOT/'docs/research/gx8002-clock-table-placement.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['table_package_offset'],hex(result['table_runtime_address']),result['sections'])
