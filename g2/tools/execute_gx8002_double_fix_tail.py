# SPDX-License-Identifier: MIT
"""Decoded signed-fix tail after unpack; entry frame modeled."""
import re

def execute(code,entry,fields,seed=0,bits=None,unpack_entry=None):
    r={f'r{i}':0x70000000+i for i in range(32)};r['r14']=0x20040000
    memory={0x20040008+off:fields.get(off,seed) for off in (0,4,8,12,16)}
    if bits is not None:r.update(r0=bits&0xffffffff,r1=bits>>32,r14=0x20040020)
    initial=r.copy()
    pc=entry;condition=False;saved=None
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r15' or bits is None or saved is not None:raise ValueError('Fix entry frame')
            saved=r['r15'];r['r14']-=4
        elif op=='bsr':
            from execute_gx8002_double_unpack import execute as unpack
            if int(args,0)!=unpack_entry or r['r0']!=0x20040000 or r['r1']!=0x20040008:raise ValueError('Fix unpack arguments')
            incoming=memory[r['r0']]|(memory[r['r0']+4]<<32)
            values=unpack(code,unpack_entry,incoming)
            for off,value in values.items():memory[r['r1']+off]=value
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=r[base]+int(off,0)
            if address not in (0x20040000,0x20040004):raise ValueError('Fix input spill')
            memory[address]=r[reg]
        elif op=='pop':
            if args!='r15' or r['r14']!=0x2004001c:raise ValueError('Fix frame endpoint')
            if bits is not None:
                if saved is None:raise ValueError('Fix missing saved link')
                r['r15']=saved;r['r14']+=4
                if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Fix ABI')
            return r['r0']
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();r[reg]=memory[r[base]+int(off,0)]
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op in ('zext','ins'):
            hi,lo=map(int,p[2:]);mask=(1<<(hi-lo+1))-1
            if op=='zext':r[p[0]]=(r[p[1]]>>lo)&mask
            else:r[p[0]]=(r[p[0]]&~(mask<<lo))|((r[p[1]]&mask)<<lo)
        elif op in ('or','nor','andi','addi','addu','subi','subu','lsl','lsr','lsli','lsri','addc'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            value=a|b if op=='or' else ~(a|b) if op=='nor' else a&b if op=='andi' else a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else (0 if b>=32 else a<<b) if op in ('lsl','lsli') else (0 if b>=32 else a>>b) if op in ('lsr','lsri') else a+b+int(condition)
            if op=='addc':condition=value>0xffffffff
            r[p[0]]=value&0xffffffff
        elif op=='btsti':condition=bool(r[p[0]]&(1<<int(p[1],0)))
        elif op=='mvc':r[p[0]]=int(condition)
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op=='add.64':
            dest,a,b=[int(x[1:]) for x in p];value=(r[f'r{a}']|(r[f'r{a+1}']<<32))+(r[f'r{b}']|(r[f'r{b+1}']<<32))
            r[f'r{dest}']=value&0xffffffff;r[f'r{dest+1}']=(value>>32)&0xffffffff
        elif op in ('cmphsi','cmphs','cmpnei','cmplti','cmplt'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0)
            condition=a>=b if op in ('cmphsi','cmphs') else a!=b if op=='cmpnei' else signed(a)<signed(b)
        elif op in ('bt','bf','br','bez','blz'):
            take=condition if op=='bt' else not condition if op=='bf' else True if op=='br' else r[p[0]]>=0x80000000 if op=='blz' else r[p[0]]==0
            if take:following=int(p[-1],0)
        else:raise ValueError('Pack instruction '+op)
        pc=following
    raise ValueError('Pack execution bound')
