# SPDX-License-Identifier: MIT
"""Qualify and link recovered UART transmit start/stop functions for admission."""
import json,subprocess
from pathlib import Path
from verify_gx8002_uart_transmit_control import verify as core,ROOT,sha
from verify_gx8002_logging import check_paths
from build_transparent_image import Elf32


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);qualification=core();candidate=qualification['candidate']
    output=Path(output) if output else ROOT/'build/gx8002-uart-transmit-control-source'
    output.mkdir(parents=True,exist_ok=True)
    rows=[];sections=[]
    for item,kind in zip(candidate['functions'],('start','stop')):
        if not item['fits']:raise ValueError('Transmit control envelope')
        section='.'+kind
        sections.append(f"{section} {item['package_offset']+0x101f6a74:#x} : {{ *(.text.{item['symbol']}) }}")
        row={k:item[k] for k in ('symbol','compiled_bytes','compiled_sha256')};row['section_name']=section
        row['stock_occurrences']=[{'symbol':item['symbol'],'package_offset':item['package_offset'],'bytes':item['envelope_bytes'],'sha256':item['stock_sha256'],'region':'image_a_xip_text'}]
        rows.append(row)
    script=output/'control.ld';script.write_text('SECTIONS { '+ ' '.join(sections)+' /DISCARD/ : { *(.text*) } }\nopen_cfw_gx8002_uart_descriptors = 0x20026a94;\nopen_cfw_gx8002_irq_save = 0x10025560;\nopen_cfw_gx8002_irq_restore = 0x1002556c;\n')
    target=output/'control.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(script),str(ROOT/'build/gx8002-uart-transmit-control/control.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target))
    for row in rows:
        section=next(s for s in elf.sections if s['name']==row['section_name'])
        if sha(elf.contents(section))!=row['compiled_sha256'] or elf.relocations(section['index']):raise ValueError('Transmit control combined link changed')
    return {'functions':rows,'qualification':qualification,'source_admitted':True,'hardware_qualified':False,
        'evidence_sha256':{name:sha((ROOT/'tools'/name).read_bytes()) for name in ('verify_gx8002_uart_transmit_control_source.py','verify_gx8002_uart_transmit_control.py','build_gx8002_uart_transmit_control.py','verify_gx8002_memcpy_source.py')},
        'limits':['Finite ordered descriptor/MMIO and IRQ token checks. Physical UART and concurrent interrupt delivery unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-transmit-control-source-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Transmit control admission passed')
