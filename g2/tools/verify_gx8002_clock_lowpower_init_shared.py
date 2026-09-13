# SPDX-License-Identifier: MIT
"""Shared-setter candidate against decoded stock/upstream policy evidence."""
import json
from itertools import product
from verify_gx8002_clock_lowpower_init import verify as baseline,execute,expected
from build_gx8002_clock_lowpower_init_shared_candidate import build,ROOT
from verify_gx8002_memcpy_source import decode

def verify():
    prior=baseline();candidate=build();code=decode((ROOT/'build/gx8002-board/clock-lowpower-init-shared-candidate.disassembly.txt').read_text());cases=0
    for a,b,c,pmu in product((0,1,2,0xffffffff),(0,3,4,0xffffffff),(0,5,6,0xffffffff),(0,64,0xffffffff,0xffffffbf)):
        answers={2:a,7:b,8:c};assert execute(code,0x1002599c,answers,pmu)==expected(answers,pmu);cases+=1
    return {'candidate':candidate,'baseline':prior,'cases':cases,'source_admitted':False,'limits':['Shared setter candidate matches the independent routing model qualified against stock/upstream outer instructions. Integer ABI and conditional PMU reads checked; nested state transitions and physical timing remain outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-lowpower-init-shared.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
