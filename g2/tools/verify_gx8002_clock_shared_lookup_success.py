# SPDX-License-Identifier: MIT
"""Shared successful lookup and low-frequency caller using actual records."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode
from analyze_gx8002_upstream_objects import IMAGE


def verify():
    placement=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'shared successful lookup')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    records=elf.contents(next(s for s in elf.sections if s['name']=='.data.gx_clock_param_table'))
    if records!=IMAGE.read_bytes()[0x186f4:0x18894]:raise ValueError('Successful lookup records')
    count=0
    for module,source in product(range(10,26),(0,1<<18)):
        result,calls=execute(code,table,module,0,0,source,lookup_records=records)
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        if result!=(1024000 if source else 12288000) or calls!=[('lookup',mapped)]:raise ValueError('Shared lookup success')
        count+=1
    return {'placement':placement,'decoded_cases':count,'source_admitted':False,
            'limits':['Actual source records and shared caller/lookup machine, fixed low selection for modules 10..25. Divider/PLL routes and stock full-machine comparison pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-shared-lookup-success.json').write_text(json.dumps(report,indent=2)+'\n');print('Shared lookup success cases:',report['decoded_cases'])
