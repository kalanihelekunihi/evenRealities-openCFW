# SPDX-License-Identifier: MIT
"""Exact callback and independent logging/lock mutation oracle."""
import json
from itertools import product
from build_gx8002_app_gpio_event import build,ROOT,Elf32
from execute_gx8002_max_decoder import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();path=ROOT/'build/gx8002-app-gpio-event/candidate.elf';elf=Elf32(path.read_bytes(),str(path));code=decode((path.parent/'candidate.disassembly.txt').read_text())
    if candidate['compiled_sha256']!=candidate['stock_sha256']:raise ValueError('Exact callback mismatch')
    cases=0
    for lock,mutation,value,result in product((0,1,31,32,0xffffffff),(0,0x10206c24,0x102077a8),(0,7,0xffffffff),(0,1,0xffffffff)):
        m={0x2002e8bc+i:0xa5 for i in range(40)};word(m,0x2002e8cc,lock)
        def helper(t,args,memory,events):
            if t==0x10206c24:events.append(('log',*args[:3]))
            elif t==0x102077a8:events.append(('lock',args[0]))
            else:raise ValueError('Helper')
            if t==mutation:word(memory,0x2002e8cc,value);word(memory,0x2002e8d0,value)
            return result
        expected=m.copy();events=[];helper(0x10206c24,[0x1020b447,0x1020b40b,124,0],expected,events);helper(0x102077a8,[word(expected,0x2002e8cc),0,0,0],expected,events);word(expected,0x2002e8d0,2000)
        ret,actual,trace=execute(code,0x10208e20,0,0,m,helper)
        if (ret,actual,[x for x in trace if x[0]!='write_byte'])!=(('return',0),expected,events):raise ValueError('GPIO event mismatch')
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Byte-exact C plus independent helper-mutation oracle. Power-lock implementation, GPIO timing and concurrency not executed here.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-app-gpio-event-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
