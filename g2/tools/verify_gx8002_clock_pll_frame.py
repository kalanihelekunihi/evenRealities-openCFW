# SPDX-License-Identifier: MIT
"""Continuous PLL/table/DTO/divider candidate paths with modeled helpers."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode,MASK
from model_gx8002_clock_pll_frequency import frequency


def verify():
    placement=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'pll frame')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    subband=struct.unpack('<4I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.subband_hz')))
    if subband!=(61440000,73728000,86016000,98304000):raise ValueError('PLL frame table identity')
    count=0
    for words,present,dto,div in product(((0,59,0,0,0),(63,2047,0,0,48),(0,0,0,0,0),(1,95,1,7,16)),(False,True),(0,0x1ffffff,0x8000000),(0,2,65536)):
        result,calls=execute(code,table,10,0,4,1,div,16,present,dto,words)
        hz=frequency(*words);wanted_calls=[('lookup',10)]
        if hz!=MASK:
            if present and not dto&(1<<27):hz=((dto&0x1ffffff)*hz)>>25
            if div:hz//=div
            wanted_calls.append(('divider',div))
        if (result,calls)!=(hz,wanted_calls):raise ValueError('PLL continuous frame mismatch')
        count+=1
    return {'placement':placement,'decoded_cases':count,'source_admitted':False,
            'limits':['Continuous candidate frame with modeled lookup/divider and fixed valid descriptors. No stock continuous-frame comparison, concurrent MMIO or hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-pll-frame.json').write_text(json.dumps(report,indent=2)+'\n');print('PLL frame cases:',report['decoded_cases'])
