# SPDX-License-Identifier: MIT
"""Decoded stock UART body-copy slice with explicit continuation boundaries."""
import re


def execute(code,memory,registers,entry=0x112b8,helper_result=0):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=0x20040000
    r.update(registers)
    initial=r.copy();pc=entry;condition=False;writes=[]
    for _ in range(2000):
        if pc in (0x112fa,):return pc,r,writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subu','subi','lsli','mula.32.l'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            value=(a+b if op in ('addu','addi') else a-b if op in ('subu','subi') else a<<b if op=='lsli' else r[p[0]]+a*b)
            r[p[0]]=value&0xffffffff
        elif op=='and':r[p[0]]=r[p[-2] if len(p)==3 else p[0]] & r[p[-1]]
        elif op=='bsr':
            target=int(args,0)
            if target==0xcc18:writes.append(('restart',r['r0'],r['r1'],r['r2']))
            elif target==0xcc4c:writes.append(('stop',r['r0']))
            elif target==0xcd0c:
                priv=sum(memory[r['r14']+i]<<(8*i) for i in range(4))
                writes.append(('async',r['r0'],r['r1'],r['r2'],r['r3'],priv))
            elif target==0xffe2f744:
                if r['r0']!=0x2002ecc4:raise ValueError('Completion queue address')
                packet=bytes(memory[r['r1']+i] for i in range(32))
                writes.append(('queue',packet.hex()))
            else:raise ValueError('Scheduling helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=helper_result
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op in ('cmpne','cmpnei','cmphs','cmphsi'):
            b=r[p[1]] if p[1] in r else int(p[1],0)
            condition=r[p[0]]>=b if op in ('cmphs','cmphsi') else r[p[0]]!=b
        elif op=='mvc':r[p[0]]=int(condition)
        elif op in ('bf','bt','br'):
            if op=='br' or condition==(op=='bt'):jump=int(p[0],0)
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            if (r[p[0]]==0)==(op=='bez'):jump=int(p[1],0)
        elif op=='str.b':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args)
            if not m:raise ValueError('Copy indexed store')
            reg,base,index=m.groups();addr=(r[base]+r[index])&0xffffffff
            if addr not in memory:raise ValueError('Copy write outside memory')
            writes.append((addr,1,r[reg]));memory[addr]=r[reg]&255
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
