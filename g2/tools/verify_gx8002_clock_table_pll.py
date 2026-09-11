# SPDX-License-Identifier: MIT
"""Decoded source-table PLL slice; no firmware admission."""
import json
import struct
from itertools import product
from link_gx8002_clock_frequency_table_probe import build,ROOT,Elf32
from verify_gx8002_clock_pll_slice import execute,frequency,decode


def verify():
    candidate=build();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    elf=Elf32((out/'analysis.elf').read_bytes(),'table PLL')
    section=next(s for s in elf.sections if s['name']=='.rodata.subband_hz')
    values=struct.unpack('<4I',elf.contents(section))
    if values!=(61440000,73728000,86016000,98304000):raise ValueError('Source frequency constants')
    table={section['address']+4*i:v for i,v in enumerate(values)}
    code=decode((out/'analysis.disassembly.txt').read_text());count=0
    for words in product((0,1,31,63),(0,59,95,255,2047),(0,1,31),(0,7),(0,16,32,48)):
        reads,result=execute(code,0x100252ec,(0x10025374,0x10025246),words,table)
        if result!=frequency(*words) or [a for a,v in reads]!=[0xa000501c,0xa0005020,0xa0005024,0xa0005028,0xa0005030]:
            raise ValueError('Table PLL mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,
            'limits':['PLL slice only; table contents and bounded table accesses checked, MMIO order checked. No complete function or hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-table-pll-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Table PLL cases:',report['decoded_cases'])
