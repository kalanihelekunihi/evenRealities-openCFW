# SPDX-License-Identifier: MIT
"""Decoded counter conversion against modulo-64 multiplication and division."""
import json,random,re
from build_gx8002_clock_time_us_candidate import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,low,high,divider_code):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();trace=[];pc=0x17870;memory={};saved=None
    from execute_gx8002_div64 import execute as divide
    for _ in range(80):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            assert args=='r15';saved=r['r15'];r['r14']-=4
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op=='movih':r[p[0]]=int(p[1],0)<<16
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('lsli','lsri'):r[p[0]]=((r[p[1]]<<int(p[2],0)) if op=='lsli' else r[p[1]]>>int(p[2],0))&MASK
        elif op in ('ld.w','st.w'):
            dest,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if a in (0xa0400044,0xa0400048):
                assert op=='ld.w';r[dest]=low if a==0xa0400044 else high;trace.append((a,r[dest]))
            else:
                assert 0x2006ffe8<=a<0x20070000
                if op=='st.w':memory[a]=r[dest]
                else:r[dest]=memory[a]
        elif op=='mul.u32':
            d=int(p[0][1:]);v=r[p[1]]*r[p[2]];r[p[0]]=v&MASK;r[f'r{d+1}']=v>>32
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op in ('br','bnez'):
            if op=='br' or r[p[0]]!=0:pc=int(p[-1],0);continue
        elif op=='bsr':
            assert int(args,0)+0x1000dfec==0x102098b4 and r['r1']==1024
            a=r['r0'];n=memory[a]|memory[a+4]<<32;buf={a+i:v for i,v in enumerate(n.to_bytes(8,'little'))}
            ret,after,events=divide(divider_code,0x12e40,[a,1024],buf,lambda *args:None)
            assert ret==('return',n%1024) and set(after)==set(buf)
            q=int.from_bytes(bytes(after[a+i] for i in range(8)),'little');assert q==n//1024
            memory[a]=q&MASK;memory[a+4]=q>>32
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=ret[1]
        elif op=='pop':
            assert args=='r15';r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert trace==[(0xa0400044,low),(0xa0400048,high)]
            return r['r0']|(r['r1']<<32)
        else:raise ValueError((op,args))
        pc+=width
    raise AssertionError('Execution bound')
