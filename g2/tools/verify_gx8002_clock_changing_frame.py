# SPDX-License-Identifier: MIT
"""Continuous frame with changing clock-selection reads."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode
from verify_gx8002_clock_selection import expected


def verify():
    evidence=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'changing frame')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    count=0
    for module,bits in product(range(26),product(range(4),repeat=3)):
        values=tuple(b<<4 for b in bits);reads=[]
        result,calls=execute(code,table,module,0,4,0,2,0,False,0,None,values,reads)
        mapped={17:16,18:16,20:19,21:19,23:22,24:22,25:10}.get(module,module)
        if module in (7,8):wanted=(0,[],[])
        else:
            trace,kind,hz=expected(mapped,4,0,values)
            wanted=(hz if kind=='return' else hz//2,[('lookup',mapped)]+([] if kind=='return' else [('divider',2)]),trace)
        if (result,calls,reads)!=wanted:raise ValueError('Changing-frame mismatch')
        count+=1
    return {'placement':evidence,'decoded_cases':count,'source_admitted':False,
            'limits':['Continuous candidate frame and changing selection MMIO; valid fixed descriptors and modeled lookup/divider. Source word fixed to non-PLL selection. No hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-changing-frame.json').write_text(json.dumps(report,indent=2)+'\n');print('Changing-frame cases:',report['decoded_cases'])
