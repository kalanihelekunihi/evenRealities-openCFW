# SPDX-License-Identifier: MIT
"""Bounded decoded preparation helper, with caller-provided target memory."""
import re


def execute(code,memory,entry=0x10302000):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=0x20040000
    initial=r.copy();pc=entry;condition=False;writes=[]
    for _ in range(500):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subu','subi','lsli','mula.32.l'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            value=(a+b if op in ('addu','addi') else a-b if op in ('subu','subi') else a<<b if op=='lsli' else r[p[0]]+a*b)
            r[p[0]]=value&0xffffffff
        elif op in ('cmpne','cmpnei','cmphs'):
            b=r[p[1]] if p[1] in r else int(p[1],0)
            condition=r[p[0]]>=b if op=='cmphs' else r[p[0]]!=b
        elif op=='mvc':r[p[0]]=int(condition)
        elif op in ('bf','bt','br'):
            if op=='br' or condition==(op=='bt'):jump=int(p[0],0)
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            if (r[p[0]]==0)==(op=='bez'):jump=int(p[1],0)
        elif op.startswith(('ld.','st.')):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Preparation memory operand')
            reg,base,off=m.groups();addr=(r[base]+int(off,0))&0xffffffff;size={'.b':1,'.h':2,'.w':4}[op[-2:]]
            if op.startswith('ld'):r[reg]=sum(memory[addr+i]<<(8*i) for i in range(size))
            else:
                if any(addr+i not in memory for i in range(size)):raise ValueError('Preparation write outside modeled memory')
                writes.append((addr,size,r[reg]))
                for i in range(size):memory[addr+i]=(r[reg]>>(8*i))&255
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Preparation ABI changed')
            return r['r0'],writes
        else:raise ValueError('Preparation instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Preparation instruction bound')
