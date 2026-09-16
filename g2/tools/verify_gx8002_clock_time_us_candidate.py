# SPDX-License-Identifier: MIT
"""Decoded counter conversion against modulo-64 multiplication and division."""
import json,random,re
from build_gx8002_clock_time_us_candidate import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,low,high,entry=0x1002585c):
    r={f'r{i}':0x12340000+i for i in range(32)};initial=r.copy();trace=[];pc=entry
    for _ in range(40):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='movih':r[p[0]]=int(p[1],0)<<16
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('lsli','lsri'):r[p[0]]=((r[p[1]]<<int(p[2],0)) if op=='lsli' else r[p[1]]>>int(p[2],0))&MASK
        elif op=='ld.w':
            dest,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            assert a in (0xa0400044,0xa0400048);r[dest]=low if a==0xa0400044 else high;trace.append((a,r[dest]))
        elif op=='mul.u32':
            d=int(p[0][1:]);v=r[p[1]]*r[p[2]];r[p[0]]=v&MASK;r[f'r{d+1}']=v>>32
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert trace==[(0xa0400044,low),(0xa0400048,high)]
            return r['r0']|(r['r1']<<32)
        else:raise ValueError((op,args))
        pc+=width
    raise AssertionError('Execution bound')

def verify():
    candidate=build();code=decode((ROOT/'build/gx8002-board/clock-time-us-candidate.disassembly.txt').read_text());rng=random.Random(909)
    values=[0,1,1023,1024,4294967,4294968,0xffffffff,1<<32,(1<<64)//1000-1,(1<<64)//1000,(1<<64)//1000+1,(1<<64)-1]+[rng.getrandbits(64) for _ in range(2048)]
    for ticks in values:assert execute(code,ticks&MASK,ticks>>32)==((ticks*1000)&((1<<64)-1))//1024
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Decoded source, MMIO order and integer ABI checked against independent integer arithmetic. Stock decoded comparison and wrapper integration remain outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-time-us-candidate-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
