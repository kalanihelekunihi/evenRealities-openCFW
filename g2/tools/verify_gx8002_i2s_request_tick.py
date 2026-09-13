# SPDX-License-Identifier: MIT
"""Independent request and signed countdown oracle."""
import json,subprocess
from itertools import product
from build_gx8002_i2s_request_tick import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_i2s_request_tick import execute
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
APP,REQUEST,MODE=0x2002e8c4,0x2002e92c,0x2002e930

def verify():
    candidate=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x12748','--stop-address=0x127e4',str(path)],text=True));new=decode((ROOT/'build/gx8002-i2s-request-tick/candidate.disassembly.txt').read_text());cases=0
    for request,mode,countdown,enabled,result in product((0,1,2),(0,1,2,255),(0,1,9,10,11,0x7fffffff,0x80000000,0xffffffff),(0,1),(0,0xffffffff)):
        m={APP+i:0xa5 for i in range(32)};m[MODE]=mode
        for a,v in ((REQUEST,request),(APP+8,7),(APP+12,countdown),(APP+20,enabled)):word(m,a,v)
        expected=m.copy();wanted=[('poll',)]
        if request==1:
            wanted.append(('print',0x1020b5a4,mode))
            if mode==1:wanted.extend([('lock',7),('print',0x1020b5d4),('start',),('ack',)]);word(expected,REQUEST,0)
            elif mode==0:wanted.extend([('stop',),('ack',),('unlock',7),('print',0x1020b5fb),('delay',13)]);word(expected,REQUEST,0)
        if 0<countdown<0x80000000:
            count=(countdown-10)&0xffffffff;word(expected,APP+12,count)
            if (count==0 or count>=0x80000000) and not enabled:wanted.extend([('print',0x1020b624),('unlock',7)]);word(expected,APP+12,0)
        def helper(t,a,mem,events,sp):
            if t==0x10206c24:events.append(('print',a[0],a[1]) if a[0]==0x1020b5a4 else ('print',a[0]))
            else:
                name={0x102097c8:'poll',0x10209770:'ack',0x10208ff0:'start',0x1020913c:'stop',0x102077a8:'lock',0x102077d4:'unlock',0x10207808:'delay'}[t];events.append((name,a[0]) if name in ('lock','unlock','delay') else (name,))
            return result
        for code,entry in ((old,0x12748),(new,0x102091bc)):
            ret,actual,events=execute(code,entry,[],m,helper);events=[e for e in events if e[0]!='write_byte']
            if (ret,actual,events)!=(('return',0),expected,wanted):raise ValueError(('Tick mismatch',request,mode,countdown,enabled,result,hex(entry)))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Independent baseline with modeled helpers and integer ABI; helper mutations and nested device behavior remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-i2s-request-tick-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
