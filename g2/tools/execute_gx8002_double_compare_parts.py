# SPDX-License-Identifier: MIT
import re

def execute(code,entry,left,right):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=0x20040000,r1=0x20040100);initial=r.copy()
    memory={base+off:value for base,fields in ((0x20040000,left),(0x20040100,right)) for off,value in fields.items()}
    pc=entry;condition=False
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(100):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];following=pc+width
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Compare ABI')
            return signed(r['r0'])
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();r[reg]=memory[r[base]+int(off,0)]
        elif op in ('subu','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);r[p[0]]=(a-b)&0xffffffff
        elif op in ('cmphs','cmpne','cmpnei','cmplt'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphs' else signed(a)<signed(b) if op=='cmplt' else a!=b
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):following=int(args,0)
        else:raise ValueError('Compare instruction '+op)
        pc=following
    raise ValueError('Compare bound')
