# SPDX-License-Identifier: MIT
"""Differential request tick helper mutations."""
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
    for mode,stage,field,value in product((0,1,2),('poll','request_log','lock','lock_log','start','stop','ack','unlock','unlock_log','delay','timeout_log'),(REQUEST,MODE,APP+8,APP+12,APP+20),(0,1,11,0xffffffff)):
        m={APP+i:0xa5 for i in range(32)};m[MODE]=mode
        for a,v in ((REQUEST,1),(APP+8,7),(APP+12,10),(APP+20,0)):word(m,a,v)
        runs=[]
        def helper(t,a,mem,events,sp):
            if t==0x10206c24:
                name={0x1020b5a4:'request_log',0x1020b5d4:'lock_log',0x1020b5fb:'unlock_log',0x1020b624:'timeout_log'}[a[0]]
                events.append(('print',a[0],a[1]) if a[0]==0x1020b5a4 else ('print',a[0]))
            else:
                name={0x102097c8:'poll',0x10209770:'ack',0x10208ff0:'start',0x1020913c:'stop',0x102077a8:'lock',0x102077d4:'unlock',0x10207808:'delay'}[t];events.append((name,a[0]) if name in ('lock','unlock','delay') else (name,))
            if name==stage:
                if field==MODE:mem[field]=value&255
                else:word(mem,field,value)
            return 0xffffffff
        for code,entry in ((old,0x12748),(new,0x102091bc)):
            ret,actual,events=execute(code,entry,[],m,helper);events=[e for e in events if e[0]!='write_byte']
            runs.append((ret,actual,events))
        if runs[0]!=runs[1]:raise ValueError(('Mutation mismatch',mode,stage,field,value,runs))
        cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Differential helper mutations; nested hardware behavior remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-i2s-request-tick-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
