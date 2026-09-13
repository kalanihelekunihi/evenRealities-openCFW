# SPDX-License-Identifier: MIT
"""Differential bionic helper mutations; no independent mutation oracle."""
import json,subprocess,math
from itertools import product
from build_gx8002_bionic_run_candidate import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_bionic_run import execute,bits,floating,signed
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
BASE=0x2002e84c
CTX=0x20040000
HEADER=0x20040100
LIST=0x2002e79c

def verify():
    candidate=build();w=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(w.read_bytes(),'stock')
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x12104','--stop-address=0x12180',str(w)],text=True));new=decode((ROOT/'build/gx8002-bionic-run/candidate.disassembly.txt').read_text());cases=0
    for target,address,value in product((0x100264dc,0x10206c24),(BASE+4,BASE+12,LIST,HEADER+28,HEADER+36),(0,1,0xffffffff,0x43150000)):
        count,counter,frame,frames,offset=2,10000,10,10,149.
        m={a+i:0xa5 for a,n in ((BASE-8,32),(CTX,32),(HEADER,80),(LIST,8)) for i in range(n)};word(m,CTX,HEADER);word(m,HEADER+28,frame);word(m,HEADER+36,frames);word(m,LIST,count);word(m,BASE+12,counter);word(m,BASE+4,bits(offset));wanted=m.copy();events=[]
        def helper(t,args,f,sp,mem,trace):
            if t==target:word(mem,address,value)
            if t==0x100264dc:return LIST,None
            if t==0x10206c24:trace.append(tuple(args[:2]));return 0,None
            raise ValueError('Helper')
        outcomes=[]
        for code,entry in ((old,0x12104),(new,0x10208b78)):
            result,actual,trace=execute(code,entry,CTX,0,m,helper)
            outcomes.append((result,actual,[x for x in trace if x[0]!='write_byte']))
        if outcomes[0]!=outcomes[1]:raise ValueError(('Bionic mutation mismatch',hex(target),hex(address),value,outcomes))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Differential bounded helper-boundary changes to state/count/header fields. Not an independent oracle or physical concurrency qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-bionic-run-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
