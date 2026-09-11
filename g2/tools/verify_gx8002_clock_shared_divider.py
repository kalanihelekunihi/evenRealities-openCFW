# SPDX-License-Identifier: MIT
"""Clock and divider execute in the same decoded register/memory state."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode
from verify_gx8002_clock_divider import build,expected


def verify():
    placement=analyze();divider=build();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    code.update(decode((ROOT/'build/gx8002-board/clock-divider-candidate.disassembly.txt').read_text()))
    elf=Elf32((out/'placement.elf').read_bytes(),'shared divider')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    count=0
    for select,present,shift,mask,word in product((0,16,32),(False,True),(0,15,31),(0,0x3ff,0xffff),(0,1,0xffffffff)):
        descriptor=(present,0x80,shift,mask,word)
        _,div=expected(present,0xa0300000,0x80,shift,mask,word)
        result,calls=execute(code,table,0,0,4,0,0,select,divider_descriptor=descriptor)
        hz={0:12288000,16:24576000,32:32000}[select]
        if result!=(hz//div if div else hz) or calls!=[('lookup',0),('divider',div)]:raise ValueError('Shared divider mismatch')
        count+=1
    return {'placement':placement,'divider':divider,'decoded_cases':count,'source_admitted':False,
            'limits':['Shared caller/divider machine state; lookup and valid descriptors modeled. Other paths and stock shared-state comparison pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-shared-divider.json').write_text(json.dumps(report,indent=2)+'\n');print('Shared divider cases:',report['decoded_cases'])
