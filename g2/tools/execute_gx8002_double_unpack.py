# SPDX-License-Identifier: MIT
"""Decoded pack execution for normalized unsigned integer inputs only."""
import re

def execute(code,entry,bits,seed=0):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=0x20040000,r1=0x20040100,r14=0x20050000)
    initial=r.copy();memory={0x20040000+i:(bits>>(8*i))&255 for i in range(8)}
    writes={}
    pc=entry;condition=False;saved=None
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Unpack ABI')
            return writes
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('ld.w','ld.h','ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='st.w':
                for i in range(4):memory[address+i]=(r[reg]>>(8*i))&255
                if 0x20040100<=address<0x20040114:writes[address-0x20040100]=r[reg]
                elif address!=0x2004fffc:raise ValueError('Unpack write outside frame')
            else:r[reg]=sum(memory[address+i]<<(8*i) for i in range(4 if op=='ld.w' else 2 if op=='ld.h' else 1))
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op in ('zext','ins'):
            hi,lo=map(int,p[2:]);mask=(1<<(hi-lo+1))-1
            if op=='zext':r[p[0]]=(r[p[1]]>>lo)&mask
            else:r[p[0]]=(r[p[0]]&~(mask<<lo))|((r[p[1]]&mask)<<lo)
        elif op in ('or','nor','andi','addi','subi','lsli','lsri','addc'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            value=a|b if op=='or' else ~(a|b) if op=='nor' else a&b if op=='andi' else a+b if op=='addi' else a-b if op=='subi' else a<<b if op=='lsli' else a>>b if op=='lsri' else a+b+int(condition)
            if op=='addc':condition=value>0xffffffff
            r[p[0]]=value&0xffffffff
        elif op=='add.64':
            dest,a,b=[int(x[1:]) for x in p];value=(r[f'r{a}']|(r[f'r{a+1}']<<32))+(r[f'r{b}']|(r[f'r{b+1}']<<32))
            r[f'r{dest}']=value&0xffffffff;r[f'r{dest+1}']=(value>>32)&0xffffffff
        elif op in ('cmphsi','cmphs','cmpnei','cmplti','cmplt'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0)
            condition=a>=b if op in ('cmphsi','cmphs') else a!=b if op=='cmpnei' else signed(a)<signed(b)
        elif op in ('bt','bf','br','bez','bnez'):
            take=condition if op=='bt' else not condition if op=='bf' else True if op=='br' else r[p[0]]!=0 if op=='bnez' else r[p[0]]==0
            if take:following=int(p[-1],0)
        else:raise ValueError('Pack instruction '+op)
        pc=following
    raise ValueError('Pack execution bound')
