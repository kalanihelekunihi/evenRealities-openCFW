# SPDX-License-Identifier: MIT
"""Continuous 24 MHz/DTO/divider candidate execution."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode


def verify():
    evidence=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'dto frame')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    count=0
    for module,present,word,div in product((0,2,10,17,25),(False,True),(0,1,0x1ffffff,0x8000000,0xffffffff),(0,2,65536)):
        result,calls=execute(code,table,module,0,4,0,div,16,present,word)
        hz=24576000
        if present and not word&(1<<27):hz=((word&0x1ffffff)*hz)>>25
        if div:hz//=div
        mapped={17:16,25:10}.get(module,module)
        if result!=hz or calls!=[('lookup',mapped),('divider',div)]:raise ValueError('DTO continuous frame mismatch')
        count+=1
    return {'placement':evidence,'decoded_cases':count,'source_admitted':False,
            'limits':['Continuous candidate frame; fixed valid DTO/lookup descriptors and modeled helper bodies. PLL and hardware not qualified by this check.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-dto-frame.json').write_text(json.dumps(report,indent=2)+'\n');print('DTO frame cases:',report['decoded_cases'])
