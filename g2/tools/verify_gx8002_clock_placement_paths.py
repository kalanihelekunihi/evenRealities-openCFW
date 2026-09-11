# SPDX-License-Identifier: MIT
"""Decoded checks using proposed actual firmware addresses; no admission."""
import json
import struct
from itertools import product
from analyze_gx8002_clock_table_placement import analyze,ROOT,Elf32
from verify_gx8002_clock_pll_slice import execute as pll,frequency,decode
from verify_gx8002_frequency_dispatch import execute as dispatch,expected as dispatch_expected
from verify_gx8002_clock_selection import execute as selection,expected as selection_expected
from verify_gx8002_clock_dto_slice import execute as dto,expected as dto_expected,MASK
from verify_gx8002_clock_frequency_return import execute as epilogue,PARAM,BASE


def verify():
    evidence=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    elf=Elf32((out/'placement.elf').read_bytes(),'placement paths')
    code=decode((out/'placement.disassembly.txt').read_text())
    switch=next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')
    table=next(s for s in elf.sections if s['name']=='.rodata.subband_hz')
    values=struct.unpack('<4I',elf.contents(table))
    if values!=(61440000,73728000,86016000,98304000):raise ValueError('Placement constants')
    memory={table['address']+i*4:v for i,v in enumerate(values)}
    counts=dict(dispatch=0,selection=0,pll=0,dto=0,epilogue=0)
    for module in (*range(256),0x7fffffff,0x80000000,MASK):
        if dispatch(code,0x10025210,module,elf.contents(switch),switch['address'],0)!=dispatch_expected(module):raise ValueError('Placement dispatch')
        counts['dispatch']+=1
    for module,offset,source,bits in product(range(26),(0,4,15,30),(0,1,1<<18,(1<<18)|1),product(range(4),repeat=3)):
        values=tuple(b<<offset for b in bits)
        if selection(code,True,module,offset,source,values,{0x10025246:'return',0x100252a6:'divider',0x100252ec:'pll',0x10025374:'dto'})!=selection_expected(module,offset,source,values):raise ValueError('Placement selection')
        counts['selection']+=1
    for words in product((0,1,31,63),(0,59,95,255,2047),(0,1,31),(0,7),(0,16,32,48)):
        reads,result=pll(code,0x100252ec,(0x10025374,0x10025246),words,memory)
        if result!=frequency(*words) or [a for a,v in reads]!=[0xa000501c,0xa0005020,0xa0005024,0xa0005028,0xa0005030]:raise ValueError('Placement PLL')
        counts['pll']+=1
    for args in product((False,True),(0,1,0x1ffffff,0x8000000,0x9ffffff,MASK),(0,1,32000,24576000,98304000,MASK)):
        if dto(code,0x10025374,0x100252a6,*args)!=dto_expected(*args):raise ValueError('Placement DTO')
        counts['dto']+=1
    for hz,div in product((0,1,32000,1024000,12288000,24576000,98304000,MASK),(0,1,2,3,32,65536,MASK)):
        if epilogue(code,0x100252a6,0,hz,div)!=([(PARAM,BASE)],hz//div if div else hz):raise ValueError('Placement return')
        counts['epilogue']+=1
    return {'placement':evidence,'decoded_cases':counts,'source_admitted':False,
            'limits':['Actual proposed addresses, separate slice states. Host envelope safety, shared frame/whole-function and firmware composer integration pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-placement-paths.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['decoded_cases'])
