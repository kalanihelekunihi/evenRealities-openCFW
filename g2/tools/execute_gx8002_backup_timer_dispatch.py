# SPDX-License-Identifier: MIT
"""Decoded timer dispatch with observable state, time and callback boundaries."""
import re
MASK=0xffffffff
BASE=0x200174bc

def execute(code,entry,memory,times,callback,time_runner=None):
    r={f'r{i}':0x43210000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();m=dict(memory);trace=[];pc=entry;condition=False;saved=None;ti=0
    for _ in range(1000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r10, r15';saved={f'r{i}':r[f'r{i}'] for i in (*range(4,11),15)};r['r14']-=32
        elif op=='pop':
            r.update(saved);r['r14']+=32;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));assert r['r0']==0;return trace,m
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('addu','mult'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+b if op=='addu' else a*b)&MASK
        elif op in ('lsli','asri'):
            v=r[p[1]];n=int(p[2],0);r[p[0]]=((v<<n) if op=='lsli' else ((v if v<0x80000000 else v-(1<<32))>>n))&MASK
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='add.64':
            d,a,b=[int(v[1:]) for v in p];v=((r[f'r{a}']|(r[f'r{a+1}']<<32))+(r[f'r{b}']|(r[f'r{b+1}']<<32)))&((1<<64)-1);r[f'r{d}']=v&MASK;r[f'r{d+1}']=v>>32
        elif op in ('cmpnei','cmpne','cmphs'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphs' else a!=b
        elif op in ('br','bt','bf','bez','bnez'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0);assert a in m
            if op=='ld.w':r[reg]=m[a];trace.append(('read',a,m[a]))
            else:m[a]=r[reg];trace.append(('write',a,m[a]))
        elif op in ('bsr','jsr'):
            if op=='bsr':
                assert int(args,0)+(0x10000000-0x38940 if entry<0x100000 else 0)==0x10005070
                v=times[ti];ti+=1
                if time_runner is not None:v=time_runner(v)
                trace.append(('time',v));result=(v&MASK,v>>32)
            else:
                target=r[args];argument=r['r0'];trace.append(('callback',target,argument));callback(target,argument,m);result=(0,0)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0'],r['r1']=result
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')
