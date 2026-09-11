#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Analysis link of upstream frequency logic; oversized text is never admitted."""
import json,subprocess
from build_gx8002_clock_frequency_candidate import build,ROOT
from build_transparent_image import Elf32
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA,sha


def link():
    evidence=build();out=ROOT/'build/gx8002-clock-frequency'
    # The text is oversized. Move only its switch table to an analysis address
    # to avoid overlap; this ELF is not a firmware placement artifact.
    script=out/'frequency-analysis.ld'
    script.write_text('''SECTIONS {
.text.__module_get_info 0x10024a44 : { *(.text.__module_get_info) }
.text.open_cfw_gx8002_clock_frequency 0x10025210 : { *(.text.open_cfw_gx8002_clock_frequency) }
.rodata.open_cfw_gx8002_clock_frequency 0x11000000 : { *(.rodata.open_cfw_gx8002_clock_frequency) }
.data.gx_clock_param_table 0x200266e0 : { *(.data.gx_clock_param_table) }
.data.gx_clock_dto_table 0x20026880 : { *(.data.gx_clock_dto_table) }
.data.gx_clock_div_table 0x20026884 : { *(.data.gx_clock_div_table) }
/DISCARD/ : { *(.text.open_cfw_gx8002_frequency_lookup) *(.text.open_cfw_gx8002_frequency_divider) }
}
open_cfw_gx8002_clock_divider = 0x10024ae8;
''')
    target=out/'frequency-analysis.elf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-')
    subprocess.run([pre+'ld','-T',str(script),str(out/'frequency.o'),'-o',str(target)],check=True)
    elf=Elf32(target.read_bytes(),str(target));stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Frequency stock identity')
    rows=[]
    for name,offset,size in (('__module_get_info',0x16a58,164),('open_cfw_gx8002_clock_frequency',0x17224,444)):
        section=next(s for s in elf.sections if s['name']=='.text.'+name);payload=elf.contents(section)
        if elf.relocations(section['index']):raise ValueError('Frequency unresolved relocation')
        rows.append({'symbol':name,'package_offset':offset,'runtime_address':section['address'],'compiled_bytes':len(payload),'stock_envelope_bytes':size,'fits':len(payload)<=size,'compiled_sha256':sha(payload),'stock_sha256':sha(stock[offset:offset+size])})
    (out/'frequency-analysis.disassembly.txt').write_text(subprocess.check_output([pre+'objdump','-d',str(target)],text=True))
    return {'build':evidence,'sections':rows,'analysis_jump_table_address':0x11000000,'external_bindings':{'open_cfw_gx8002_clock_divider':0x10024ae8},'source_admitted':False,'hardware_qualified':False,
            'limits':['Oversized frequency text overlaps stock gate jump-table range. Analysis jump table relocated away; never a firmware provider. Helpers and switch behavior require decoded qualification.']}

if __name__=='__main__':
    report=link();(ROOT/'docs/research/gx8002-clock-frequency-linked-candidate.json').write_text(json.dumps(report,indent=2)+'\n')
    print([(r['symbol'],r['compiled_bytes'],r['fits']) for r in report['sections']])
