# SPDX-License-Identifier: MIT
"""Shared caller/lookup machine execution with missing module records."""
import json
import struct
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode,MASK


def verify():
    placement=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'shared lookup')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    count=0
    for module in (*range(256),0x7fffffff,0x80000000,MASK):
        result,calls=execute(code,table,module,0,4,lookup_ids=[MASK]*26)
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        if result!=0 or calls!=([] if module in (7,8) else [('lookup',mapped)]):raise ValueError('Shared lookup failure')
        count+=1
    return {'placement':placement,'decoded_cases':count,'source_admitted':False,
            'limits':['Shared caller/lookup failure paths with synthetic absent IDs only. Successful lookup records and complete stock comparison pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-shared-lookup-failure.json').write_text(json.dumps(report,indent=2)+'\n');print('Shared lookup failure cases:',report['decoded_cases'])
