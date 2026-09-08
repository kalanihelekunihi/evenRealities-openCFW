#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build explicit IRQ context wrapper and ordinary C dispatcher for analysis."""
import json
import subprocess
from build_gx8002_irq_dispatch_candidate import build as authenticate
from verify_gx8002_analog_source import FLAGS
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import sha, IMAGE, IMAGE_SHA
from link_gx8002_uart_console import ROOT


def build():
    evidence=authenticate();output=ROOT/'build/gx8002-irq';sdk=ROOT/'build/upstream-nationalchip-lvp-kws'
    prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';source=ROOT/'components/shared/gx8002'
    flags=['-Os',*FLAGS[1:]];command=[str(prefix)+'gcc',*flags,'-DOPEN_CFW_GX8002_IRQ_BODY_ONLY']
    for p in ('arch/soc/grus/include','include/utility','include/utility/libc'):command+=['-isystem',str(sdk/p)]
    subprocess.run([*command,'-c',str(source/'runtime_gx8002_irq_dispatch.c'),'-o',str(output/'body.o')],check=True)
    subprocess.run([str(prefix)+'gcc','-mcpu=ck804ef','-mhard-float','-mistack','-c',str(source/'runtime_gx8002_irq_entry.S'),'-o',str(output/'entry.o')],check=True)
    script=output/'entry.ld';script.write_text('''SECTIONS {
.text 0x10025574 : { *(.text.open_cfw_gx8002_irq_entry) *(.text.open_cfw_gx8002_irq_dispatch_body) }
}
open_cfw_gx8002_irq_table = 0x20026ef4;
''')
    linked=output/'entry.elf';subprocess.run([str(prefix)+'ld','-T',str(script),str(output/'entry.o'),str(output/'body.o'),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));section=next(s for s in elf.sections if s['name']=='.text')
    if elf.relocations(section['index']) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved entry')
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA or section['address']!=0x10025574 or section['size']>80:raise ValueError('entry placement failure')
    disassembly=subprocess.check_output([str(prefix)+'objdump','-d',str(linked)],text=True);(output/'entry.disassembly.txt').write_text(disassembly)
    report={'upstream_evidence':evidence,'c_flags':flags,'entry_source_sha256':sha((source/'runtime_gx8002_irq_entry.S').read_bytes()),'compiled_bytes':section['size'],'compiled_sha256':sha(elf.contents(section)),'stock_package_offset':0x17588,'stock_envelope_bytes':80,'stock_sha256':sha(stock[0x17588:0x175d8]),'source_admitted':False,'limits':['Fits stock entry with combined r15-r31 save block, preserving r16/r17 additionally.','Software frame grows from stock 92 bytes to 100, plus four bytes in C callback path.','Register restoration and nested interrupt execution require qualification.','No hardware or nested interrupt qualification.']}
    (ROOT/'docs/research/gx8002-irq-entry-candidate.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(json.dumps(build(),indent=2))
