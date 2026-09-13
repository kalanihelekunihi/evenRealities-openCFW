# SPDX-License-Identifier: MIT
"""Bounded decoded EVAD execution; MMIO reads/writes retain their order."""
import re
STACK=0x20070000
ADDRESSES=(0xa0a00100,0xa0a00010,0xa0a00014,0xa0a00030,0xa0a00034,0xa0a00050,0xa0a00054)

def execute(code,entry,source,config,seed,busy):
    r={f'r{i}':0x98760000+i for i in range(32)}
    r.update(r0=source,r1=config[0],r2=config[1],r3=config[2],r14=STACK)
    initial=r.copy();memory={a:seed^a for a in ADDRESSES};stack={};trace=[];pc=entry;condition=False;polls=0
    status={1:0xa0a00024,2:0xa0a00044,4:0xa0a00064}.get(source)
    for _ in range(300):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('EVAD ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','movih','lrw'):
            r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi','lsli','rotli'):
            value=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0)
            r[p[0]]={'addi':lambda:value+n,'subi':lambda:value-n,'lsli':lambda:value<<n,'rotli':lambda:(value<<n)|(value>>(32-n))}[op]()&0xffffffff
        elif op=='bseti':r[p[0]]|=1<<int(p[-1],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='bnez':
            if r[p[0]]:jump=int(p[1],0)
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('EVAD memory operand')
            reg,base,off=m.groups();address=(r[base]+int(off,0))&0xffffffff
            if STACK-12<=address<STACK and address%4==0:
                if op=='ld.w':r[reg]=stack[address]
                else:stack[address]=r[reg]
            elif address==status and op=='ld.w':
                # Stop only on the actual repeated status read, not a generic
                # instruction limit; represent a nonterminating peripheral.
                if busy is None and polls==16:return 'busy',trace,memory
                r[reg]=0x80000001 if busy is None or polls<busy else 0
                polls+=1;trace.append(('read',address,r[reg]))
            elif address in memory:
                if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
                else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
            else:raise ValueError('EVAD unexpected MMIO '+hex(address))
        else:raise ValueError('EVAD instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('EVAD execution bound')
