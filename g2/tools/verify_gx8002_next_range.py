# SPDX-License-Identifier: MIT
"""Independent range arithmetic and target call oracle."""
import json,subprocess
from itertools import product
from build_gx8002_next_range_candidate import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_next_range import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word

def verify():
    candidate=build();w=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(w.read_bytes(),'stock')
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x12324','--stop-address=0x12358',str(w)],text=True));new=decode((ROOT/'build/gx8002-next-range/candidate.disassembly.txt').read_text());cases=0
    for first,last,limit,result in product((0,1,9,0x7fffffff,0xffffffff),(0,1,9,19,0x80000000,0xffffffff),(0,1,10,20,0xffffffff),(0,1,0xffffffff)):
        m={0x2002e8bc+i:0xa5 for i in range(24)};word(m,0x2002e8c4,limit);word(m,0x2002e8c8,0x20044000)
        delta=(last-first)&0xffffffff;start=(last+1)&0xffffffff;end=(start+delta)&0xffffffff
        if end>=limit:start,end=0,delta
        def helper(target,args,memory,events):
            if target!=0x10205488:raise ValueError('Helper')
            events.append((args[0],word(memory,args[1]),word(memory,args[1]+4)))
            return result
        for code,entry in ((old,0x12324),(new,0x10208d98)):
            ret,actual,events=execute(code,entry,first,last,m,helper)
            if (ret,actual,events)!=(('return',result),m,[(0x20044000,start,end)]):raise ValueError(('Range mismatch',first,last,limit,result,hex(entry)))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Guarded range and return-value oracle, no physical output timing or nested frame helper qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-next-range-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
