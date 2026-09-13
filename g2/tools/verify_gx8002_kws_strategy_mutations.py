# SPDX-License-Identifier: MIT
"""Differential keyword-selector logging mutations; no independent mutation oracle."""
import json,subprocess,math
from itertools import product
from build_gx8002_kws_strategy_candidate import build,ROOT,IMAGE_SHA,sha,Elf32
from execute_gx8002_kws_strategy import execute,bits,floating
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
BASE=0x2002e7a8
LIST=0x2002e79c
PARAM=0x20041000
CTX=0x20040000

def verify():
    candidate=build();w=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(w.read_bytes(),'stock')
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x11f9c','--stop-address=0x120e4',str(w)],text=True));new=decode((ROOT/'build/gx8002-kws-strategy/candidate.disassembly.txt').read_text());cases=0
    f32=lambda v:floating(bits(v))
    def integer(value):
        return (0 if math.isnan(value) else int(max(-2147483648,min(2147483647,value))))&0xffffffff
    for call,address,value in product((0,1,2),(BASE,LIST+4,BASE+12,BASE+32,PARAM+76,PARAM+164,CTX+8),(0,1,2)):
        count,a,b,threshold=2,51.,80.,500
        m={address+i:0 for address,n in ((LIST,12),(BASE,164),(PARAM,264),(CTX,32)) for i in range(n)};word(m,LIST+4,PARAM);word(m,BASE,count);word(m,CTX+8,123)
        for i,score in enumerate((a,b)):
            word(m,BASE+4+20*i,i);word(m,BASE+12+20*i,bits(score));word(m,PARAM+88*i+76,threshold);word(m,PARAM+88*i+80,40+i)
        def helper(t,args,f,sp,mem,events):
            if t==0x100264dc:return LIST,None
            if t!=0x10206c24:raise ValueError('helper')
            events.append(tuple(args)+(word(mem,sp),word(mem,sp+4)))
            if len(events)-1==call:
                replacement=(PARAM if value==0 else PARAM+88) if address==LIST+4 else bits(float(value)*60) if address in (BASE+12,BASE+32) else value
                word(mem,address,replacement)
            return 0,None
        outcomes=[]
        for code,entry in ((old,0x11f9c),(new,0x10208a10)):
            result,memory,events=execute(code,entry,CTX,0,m,helper)
            outcomes.append((result,memory,events))
        if outcomes[0]!=outcomes[1]:raise ValueError(('Mutation mismatch',call,hex(address),value,outcomes[0][2],outcomes[1][2]))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Differential logging-boundary mutations of count, pointer, scores, thresholds and context index. No independent mutation oracle or hardware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-strategy-mutations.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
