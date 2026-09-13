# SPDX-License-Identifier: MIT
"""Finite binary32 MAX scorer oracle and decoded stock/source comparison."""
import json, subprocess, math
from itertools import product
from build_gx8002_max_score_candidate import build, ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA, sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word
from execute_gx8002_max_score import execute, bits, floating, signed
BASE=0x2002e744
CTX=0x20040000
HEADER=0x20040100
PARAM=0x20041000
OUTPUT=0x20042000

def verify():
    candidate=build()
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x11c68','--stop-address=0x11e0c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-max-score/candidate.disassembly.txt').read_text())
    cases=0
    for count,major,index,score,threshold,history,offset in product((0,1,2),(0,1,2),(-1,0,9,10),(0.,0.4999,0.5,0.501,1.25,float('nan'),float('inf'),float('-inf'),1e30,-1e30),(-1,500),(0,1,255),(0.,0.75)):
        memory={a+i:0 for a,n in ((BASE-16,132),(CTX,32),(HEADER,80),(PARAM,176),(OUTPUT,8)) for i in range(n)}
        word(memory,BASE+4,index&0xffffffff);word(memory,BASE+88,count);word(memory,BASE+92,PARAM)
        word(memory,CTX,HEADER);word(memory,CTX+8,123);word(memory,CTX+16,OUTPUT);word(memory,HEADER+68,8)
        for i in range(2):
            word(memory,OUTPUT+4*i,bits(score));word(memory,PARAM+88*i+76,threshold&0xffffffff)
            word(memory,PARAM+88*i+80,40+i);word(memory,PARAM+88*i+84,i)
            for j in range(10):word(memory,BASE+8+8*j+4*i,history)
        def helper(t,args,f,sp,m,events):
            a,b,c,d=args
            if t==0x102099cc:
                events.append(('clear',a,b,c))
                for i in range(c):m[a+i]=b&255
                return a,None
            if t==0x10025608:events.append(('invalidate',a,b));return 0,None
            if t==0x10208c60:events.append(('output',a));return OUTPUT,None
            if t==0x10208b78:events.append(('bionic',a,b,f['fr0'],f['fr1'],c));return 0,None
            if t==0x10208b58:events.append(('offset',a,f['fr0']));return 0,bits(offset)
            if t==0x10208980:events.append(('insert',a,b,f['fr0'],c,d));return 0,None
            if t==0x10206c24:events.append(('print',a,b,c,d,word(m,sp),word(m,sp+4),word(m,sp+8)));return 0,None
            if t==0x10208b68:events.append(('reset',));return 0,None
            raise ValueError(('helper',hex(t)))
        expected=memory.copy();events=[('clear',BASE,0,2),('invalidate',OUTPUT,8),('output',OUTPUT)]
        expected[BASE]=expected[BASE+1]=0;expected[CTX+13]=0
        idx=index-int(index/10)*10
        for i in range(count):
            if i!=major:continue
            scaled=floating(bits(floating(bits(score))*1000.))
            value=0 if math.isnan(scaled) else int(max(-2147483648,min(2147483647,scaled)))
            score_bits=bits(value);th_bits=bits(threshold)
            events.append(('bionic',CTX,PARAM+88*i,score_bits,th_bits,0))
            effective=threshold
            if i:
                events.append(('offset',CTX,th_bits));effective=int(floating(bits(floating(th_bits)+floating(bits(offset)))))
            address=BASE+8+8*idx+4*i
            if value>effective:
                word(expected,BASE+96,value&0xffffffff);word(expected,address,1)
                activation=(expected[BASE+i]+sum(word(expected,BASE+8+8*j+4*i) for j in range(10)))&255
                expected[BASE+i]=activation
                if activation==1:
                    events.append(('insert',i,40+i,bits(floating(score_bits)/10.),0,0))
                    events.append(('print',0x1020b276,123,PARAM+88*i,40+i,effective&0xffffffff,value&0xffffffff,(value-effective)&0xffffffff))
                    word(expected,BASE+96,0)
                    if i:events.append(('reset',))
            else:word(expected,address,0)
        for code,entry in ((old,0x11c68),(new,0x102086dc)):
            actual=execute(code,entry,CTX,major,memory,helper)
            observed=(actual[0],actual[1],[e for e in actual[2] if e[0]!='write_byte'])
            if observed!=(('return',0),expected,events):
                raise ValueError(('MAX mismatch',count,major,index,score,threshold,history,offset,hex(entry),observed[2],events))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Binary32 results include NaN, infinities and signed saturation under pinned vendor CK804 emulator semantics. Floating exception flags/traps, alternate rounding modes and concurrent hardware behavior remain unqualified.']}
if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-max-score-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(result['decoded_cases'])
