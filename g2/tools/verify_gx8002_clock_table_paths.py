# SPDX-License-Identifier: MIT
"""Qualify fitting table candidate paths individually; no full ABI claim."""
import json
from itertools import product
from verify_gx8002_clock_table_pll import verify as pll_verify,ROOT,Elf32,decode
from verify_gx8002_frequency_dispatch import execute as dispatch,expected as dispatch_expected
from verify_gx8002_clock_selection import execute as selection,expected as selection_expected
from verify_gx8002_clock_dto_slice import execute as dto,expected as dto_expected,MASK
from verify_gx8002_clock_frequency_return import execute as epilogue,PARAM,BASE


def verify():
    evidence=pll_verify();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    elf=Elf32((out/'analysis.elf').read_bytes(),'table paths')
    code=decode((out/'analysis.disassembly.txt').read_text())
    table=elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency'))
    counts={'dispatch':0,'selection':0,'dto':0,'return':0}
    for module in (*range(256),0x7fffffff,0x80000000,MASK):
        if dispatch(code,0x10025210,module,table,0x11000000,0)!=dispatch_expected(module):raise ValueError('Table dispatch')
        counts['dispatch']+=1
    for module,offset,source,bits in product(range(26),(0,4,15,30),(0,1,1<<18,(1<<18)|1),product(range(4),repeat=3)):
        values=tuple(b<<offset for b in bits)
        got=selection(code,True,module,offset,source,values,{0x10025246:'return',0x100252a6:'divider',0x100252ec:'pll',0x10025374:'dto'})
        if got!=selection_expected(module,offset,source,values):raise ValueError('Table selection')
        counts['selection']+=1
    for args in product((False,True),(0,1,0x1ffffff,0x8000000,0x9ffffff,MASK),(0,1,32000,24576000,98304000,MASK)):
        if dto(code,0x10025374,0x100252a6,*args)!=dto_expected(*args):raise ValueError('Table DTO')
        counts['dto']+=1
    for frequency,divider in product((0,1,32000,1024000,12288000,24576000,98304000,MASK),(0,1,2,3,32,65536,MASK)):
        if epilogue(code,0x100252a6,0,frequency,divider)!=([(PARAM,BASE)],frequency//divider if divider else frequency):raise ValueError('Table return')
        counts['return']+=1
    return {'pll_evidence':evidence,'decoded_cases':counts,'source_admitted':False,
            'limits':['Separate fixed-entry slices, modeled helper return and saved frame. Whole-function composition, table placement and hardware qualification pending.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-table-paths-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report['decoded_cases'])
