# SPDX-License-Identifier: MIT
"""Shared clock/lookup/divider with source-built parameter and divider tables."""
import json
import struct
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode
from verify_gx8002_clock_divider import build
from analyze_gx8002_upstream_objects import IMAGE


def verify():
    placement=analyze();leaf=build();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text());code.update(decode((ROOT/'build/gx8002-board/clock-divider-candidate.disassembly.txt').read_text()))
    elf=Elf32((out/'placement.elf').read_bytes(),'actual clock tables')
    sections={s['name']:s for s in elf.sections}
    table=struct.unpack('<19I',elf.contents(sections['.rodata.open_cfw_gx8002_clock_frequency']))
    records=elf.contents(sections['.data.gx_clock_param_table'])
    divs=elf.contents(sections['.data.gx_clock_div_table'])
    stock=IMAGE.read_bytes()
    if records!=stock[0x186f4:0x18894] or divs!=stock[0x18898:0x188dc]:raise ValueError('Actual table identity')
    cells={}
    for i in range(26):
        for off in (8,12):cells[0x200266e0+i*16+off,4]=struct.unpack_from('<I',records,i*16+off)[0]
    for i in range(17):
        addr=0x20026884+i*4;off,shift,mask=struct.unpack_from('<BBH',divs,i*4)
        cells[addr,1]=off;cells[addr+1,1]=shift;cells[addr+2,2]=mask
        for base in (0xa0010000,0xa0300000):cells[base+off,4]=0
    count=0
    for module in range(26):
        result,calls=execute(code,table,module,0,0,lookup_records=records,source_cells=cells)
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        early=mapped>=10 or mapped in (2,6,9)
        wanted=[] if module in (7,8) else [('lookup',mapped)]+([] if early else [('divider',0)])
        if (result,calls)!=(0 if module in (7,8) else 12288000,wanted):raise ValueError('Actual tables full low path')
        count+=1
    return {'placement':placement,'divider':leaf,'decoded_cases':count,'source_admitted':False,
            'limits':['Shared candidate and both helper bodies with actual source records; zeroed selection/divider MMIO only. Other routes and stock continuous comparison pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-actual-tables.json').write_text(json.dumps(report,indent=2)+'\n');print('Actual table cases:',report['decoded_cases'])
