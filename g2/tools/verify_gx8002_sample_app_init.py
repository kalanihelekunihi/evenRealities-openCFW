# SPDX-License-Identifier: MIT
"""One-time application initialization oracle, including repeated invocations."""
import json
from itertools import product
from build_gx8002_sample_app_init import build,ROOT,Elf32
from execute_gx8002_max_decoder import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
BASE=0x2002e8c4

def verify():
    candidate=build();p=ROOT/'build/gx8002-sample-app-init/candidate.elf';code=decode((p.parent/'candidate.disassembly.txt').read_text())
    if candidate['compiled_sha256']!=candidate['stock_sha256']:raise ValueError('Exact code')
    cases=0
    for initialized,target,value,result in product((0,1,0xffffffff),(0,0x10206c24,0x102096fc,0x10207770),(0,1,0xffffffff),(0,1,0xffffffff)):
        m={BASE-8+i:0xa5 for i in range(40)};word(m,BASE+16,initialized)
        def helper(t,args,memory,events):
            if t==0x10206c24:events.append(('log',*args[:3],word(memory,BASE+16)))
            elif t==0x102096fc:events.append(('setup',word(memory,BASE+16)))
            elif t==0x10207770:events.append(('create',args[0],word(memory,BASE+16)));word(memory,args[0],7)
            else:raise ValueError('Helper')
            if t==target:word(memory,BASE+16,value);word(memory,BASE+8,value)
            return result
        for invocation in range(2):
            expected=m.copy();events=[]
            if word(expected,BASE+16)==0:
                word(expected,BASE+16,1);helper(0x10206c24,[0x1020b458,0x1020b419,349,0],expected,events);helper(0x102096fc,[0,0,0,0],expected,events);helper(0x10207770,[BASE+8,0,0,0],expected,events)
            ret,actual,trace=execute(code,0x10208e4c,0,0,m,helper)
            if (ret,actual,[x for x in trace if x[0]!='write_byte'])!=(('return',0),expected,events):raise ValueError(('Initialization mismatch',initialized,target,value,result,invocation))
            m=actual;cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Byte-exact C with independent repeated-call guard/mutation oracle. Setup and lock-create bodies modeled; hardware unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-sample-app-init-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
