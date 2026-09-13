# SPDX-License-Identifier: MIT
"""Qualify and link recovered UART abort functions for admission."""
import json,subprocess
from pathlib import Path
from verify_gx8002_uart_abort import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from build_transparent_image import Elf32


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();candidate=qualification['candidate']
    output=Path(output) if output else ROOT/'build/gx8002-uart-abort-source'
    output.mkdir(parents=True,exist_ok=True)
    rows=[];sections=[]
    for item,kind in zip(candidate['functions'],('transmit_abort_dma','receive_abort_dma','transmit_abort','receive_abort')):
        if not item['fits'] or item['compiled_sha256']!=item['stock_sha256']:raise ValueError('UART abort envelope')
        section='.'+kind
        sections.append(f"{section} {item['package_offset']+0x101f6a74:#x} : {{ *(.text.{item['symbol']}) }}")
        row={k:item[k] for k in ('symbol','compiled_bytes','compiled_sha256')};row['section_name']=section
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
        rows.append(row)
    script=output/'control.ld';script.write_text('SECTIONS { '+ ' '.join(sections)+' /DISCARD/ : { *(.text*) } }\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\nopen_cfw_gx8002_dma_abort = 0x10203b40;\n')
    target=output/'control.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(script),str(ROOT/'build/gx8002-uart-abort/control.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target))
    for row in rows:
        section=next(s for s in elf.sections if s['name']==row['section_name'])
        if sha(elf.contents(section))!=row['compiled_sha256'] or elf.relocations(section['index']):raise ValueError('UART abort combined link changed')
    return {'functions':rows,'qualification':qualification,'source_admitted':True,'hardware_qualified':False,
        'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in ('verify_gx8002_uart_abort_source.py','verify_gx8002_uart_abort.py','build_gx8002_uart_abort.py','verify_gx8002_memcpy_source.py','build_gx8002_dma_abort.py','verify_gx8002_dma_abort.py')},
        'limits':['Four byte-identical C replacements with nested mode/channel gating, DMA abort and descriptor-reset checks. DMA clear/deallocate effects modeled; hardware and concurrency unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-abort-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('UART abort admission passed')
