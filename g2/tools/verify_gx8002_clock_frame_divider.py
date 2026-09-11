# SPDX-License-Identifier: MIT
"""Continuous outer clock frame with a decoded source divider helper."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode
from verify_gx8002_clock_divider import build,execute as leaf,expected


def verify():
    evidence=analyze();divider_evidence=build();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    divider_code=decode((ROOT/'build/gx8002-board/clock-divider-candidate.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'frame divider')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    count=0
    for select,present,shift,mask,word in product((0,16,32),(False,True),(0,15,31),(0,0x3ff,0xffff),(0,1,0xffffffff)):
        args=(present,0xa0300000,0x80,shift,mask,word)
        want_reads,div=expected(*args);reads=[]
        def hook(param,base):
            if (param,base)!=(0x20031000,0xa0300000):raise ValueError('Frame divider arguments')
            trace,result=leaf(divider_code,0x10024ae8,*args);reads.extend(trace);return result
        result,calls=execute(code,table,0,0,4,0,0,select,divider_hook=hook)
        hz={0:12288000,16:24576000,32:32000}[select]
        if result!=(hz//div if div else hz) or calls!=[('lookup',0),('divider',div)] or reads!=want_reads:
            raise ValueError('Frame/source divider mismatch')
        count+=1
    return {'placement':evidence,'divider':divider_evidence,'decoded_cases':count,'source_admitted':False,
            'limits':['Continuous outer frame with separate decoded leaf frame; lookup/descriptors modeled. Shared helper register state and complete firmware not qualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-frame-divider.json').write_text(json.dumps(report,indent=2)+'\n');print('Frame/divider cases:',report['decoded_cases'])
