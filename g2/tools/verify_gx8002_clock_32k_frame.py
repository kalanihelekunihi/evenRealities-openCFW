# SPDX-License-Identifier: MIT
"""Continuous candidate frame qualification for 32 kHz selection shortcut."""
import json
import struct
from itertools import product
from verify_gx8002_clock_low_frame import execute,analyze,ROOT,Elf32,decode


def verify():
    evidence=analyze();out=ROOT/'build/gx8002-clock-frequency-table-probe'
    code=decode((out/'placement.disassembly.txt').read_text())
    elf=Elf32((out/'placement.elf').read_bytes(),'32k frame')
    table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    count=0
    for module,offset,source,div in product((0,1,6,9),(0,4,15,30),(0,1,1<<18,(1<<18)|1),(0,2,65536)):
        got=execute(code,table,module,0,offset,source,div,1<<(offset+1))
        if got!=(32000//div if div else 32000,[('lookup',module),('divider',div)]):raise ValueError('32k continuous frame mismatch')
        count+=1
    return {'placement':evidence,'decoded_cases':count,'source_admitted':False,
            'limits':['Candidate continuous frame with modeled lookup/divider and fixed valid descriptors; no hardware or complete frequency qualification.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-32k-frame.json').write_text(json.dumps(report,indent=2)+'\n');print('32k frame cases:',report['decoded_cases'])
