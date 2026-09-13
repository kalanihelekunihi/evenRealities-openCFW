# SPDX-License-Identifier: MIT
"""Stock/source keyword-selection comparison with an independent oracle."""
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
    for count,a,b,threshold in product((0,1,2),(0.,40.,49.,50.,51.,70.,float('nan'),float('inf'),float('-inf'),1e30,-1e30),(0.,49.,51.,80.,float('nan'),float('inf'),float('-inf')),(0,500,555)):
        m={address+i:0 for address,n in ((LIST,12),(BASE,164),(PARAM,176),(CTX,32)) for i in range(n)};word(m,LIST+4,PARAM);word(m,BASE,count);word(m,CTX+8,123)
        for i,score in enumerate((a,b)):
            word(m,BASE+4+20*i,i);word(m,BASE+12+20*i,bits(score));word(m,PARAM+88*i+76,threshold);word(m,PARAM+88*i+80,40+i)
        def helper(t,args,f,sp,mem,events):
            if t==0x100264dc:return LIST,None
            if t!=0x10206c24:raise ValueError('helper')
            events.append(tuple(args)+(word(mem,sp),word(mem,sp+4)))
            return 0,None
        expected=[];selected=0;best=0.;th=f32(f32(threshold)/10.)
        if count:
            for i,score in enumerate((a,b)[:count]):
                difference=f32(f32(score-f32(th-10.))*0.5) if score<th else f32(score-th)
                if score<th and not difference>=0: difference=f32(0.1)
                if difference>best:best=difference;selected=i
                expected.append((0x1020b37e,PARAM+88*i,40+i,integer(f32(10*th)),integer(f32(10*score)),integer(f32(10*difference))))
            expected.append((0x1020b39f,123,PARAM+88*selected,40+selected,integer(f32(10*th)),integer(f32(10*(a,b)[selected]))))
        for code,entry in ((old,0x11f9c),(new,0x10208a10)):
            result,memory,events=execute(code,entry,CTX,0,m,helper)
            if (result,memory,events)!=(('return',BASE+4+20*selected if count else 0),m,expected):raise ValueError(('Selection mismatch',count,a,b,threshold,hex(entry),events,expected))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Two-record oracle includes NaN/infinity/large finite results under pinned CK804 conversion semantics. Default rounding and modeled printf; mutations, exception flags/traps, invalid state and hardware remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-strategy-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
