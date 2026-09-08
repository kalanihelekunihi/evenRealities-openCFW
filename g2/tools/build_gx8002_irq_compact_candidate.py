#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Build architecture IRQ source without an extra dispatcher call frame."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32

def build():
    out=ROOT/'build/gx8002-irq';out.mkdir(exist_ok=True)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    source=ROOT/'components/shared/gx8002/runtime_gx8002_irq_compact_entry.S'
    flags=['-mcpu=ck804ef','-mhard-float','-mistack']
    subprocess.run([pre+'gcc',*flags,'-c',str(source),'-o',str(out/'compact.o')],check=True)
    script=out/'compact.ld';script.write_text('SECTIONS { .text 0x10025574 : { *(.text.open_cfw_gx8002_irq_compact_entry) } }\nopen_cfw_gx8002_irq_table = 0x20026ef4;\n')
    linked=out/'compact.elf';subprocess.run([pre+'ld','-T',str(script),str(out/'compact.o'),'-o',str(linked)],check=True)
    elf=Elf32(linked.read_bytes(),str(linked));section=next(s for s in elf.sections if s['name']=='.text')
    if elf.relocations(section['index']) or any(s['name'] and s['section']==0 for s in elf.symbols()):raise ValueError('unresolved compact entry')
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('stock changed')
    payload=elf.contents(section)
    if len(payload)>80:raise ValueError('compact entry envelope')
    (out/'compact.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(linked)],text=True))
    report={'source_sha256':sha(source.read_bytes()),'flags':flags,'compiled_bytes':len(payload),
            'compiled_sha256':sha(payload),'byte_exact':payload==stock[0x17588:0x175d8],
            'software_frame_bytes':92,'source_kind':'architecture_assembly','source_admitted':False,
            'limits':['Requires ABI-compliant callbacks; combined decoded dispatch/context checks remain before admission. No hardware qualification.']}
    (ROOT/'docs/research/gx8002-irq-compact-candidate.json').write_text(json.dumps(report,indent=2)+'\n');print(report);return report
if __name__=='__main__':build()
