# SPDX-License-Identifier: MIT
"""Decoded microsecond delay with explicit timer and backoff events."""
import re
MASK=0xffffffff

def execute(code,entry,usec,times,time_runner=None):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=usec,r14=0x20070000);initial=r.copy();m={};pc=entry;condition=False;saved=None;ti=0;trace=[];backoff=0
    for _ in range(3000):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r6, r15';saved={k:r[k] for k in ('r4','r5','r6','r15')};r['r14']-=16
        elif op=='pop':
            r.update(saved);r['r14']+=16;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return 'return',trace
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('cmpnei','cmpne','cmphs'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphs' else a!=b
        elif op=='incf':
            if not condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='add.64':
            d,a,b=[int(x[1:]) for x in p];v=((r[f'r{a}']|(r[f'r{a+1}']<<32))+(r[f'r{b}']|(r[f'r{b+1}']<<32)))&((1<<64)-1);r[f'r{d}']=v&MASK;r[f'r{d+1}']=v>>32
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(p[-1],0)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&MASK;backoff+=1
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0);assert 0x2006ffe8<=a<0x2006fff0
            if op=='st.w':m[a]=r[reg]
            else:r[reg]=m[a]
        elif op=='bsr':
            assert int(args,0)+(0x1000dfec if entry<0x100000 else 0)==0x1002585c
            if backoff:trace.append(('backoff',backoff));backoff=0
            if ti==len(times):return 'poll',trace
            v=times[ti];ti+=1
            if time_runner is not None:v=time_runner(v)
            trace.append(('time',v))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=v&MASK;r['r1']=v>>32
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')
