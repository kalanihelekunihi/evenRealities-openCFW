# SPDX-License-Identifier: MIT
"""Decoded gate query executor; nested lookup output is marshalled to its frame."""
import re
from verify_gx8002_power_initialize import word
MASK=0xffffffff

def execute(code,entry,module,table,lookup,registers):
    r={f'r{i}':0x43210000+i for i in range(32)};r.update(r0=module,r14=0x20070000)
    initial=r.copy();memory=dict(table);pc=entry;condition=False;saved=None;trace=[]
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4, r15';saved={k:r[k] for k in ('r4','r15')};r['r14']-=8
        elif op=='pop':
            assert args=='r4, r15';r.update(saved);r['r14']+=8
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert all(memory[a]==v for a,v in table.items())
            return r['r0'],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('cmphsi','cmpnei','cmpne'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphsi' else a!=b
        elif op in ('lsl','lsr'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];assert b<32;r[p[0]]=((a<<b) if op=='lsl' else a>>b)&MASK
        elif op=='asr':
            a=r[p[0] if len(p)==2 else p[1]];count=r[p[-1]]&31;r[p[0]]=((a if a<0x80000000 else a-0x100000000)>>count)&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+r[p[-1]])&MASK
        elif op=='and':r[p[0]]=r[p[0] if len(p)==2 else p[1]]&r[p[-1]]
        elif op=='nor':r[p[0]]=~(r[p[0]]|r[p[1]])&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('br','bt','bf','bez','bnez'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','ld.bs'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if a in registers:
                assert op=='ld.w';r[reg]=registers[a];trace.append(('read',a,r[reg]))
            elif op=='ld.w':r[reg]=word(memory,a)
            else:
                v=memory[a];r[reg]=(v if v<128 else v-256)&MASK
        elif op=='bsr':
            assert int(args,0)+(0x1000dfec if entry<0x100000 else 0)==0x10024a44
            assert r['r0']==module;dest=r['r1'];assert 0x2006ff80<=dest and dest+24<=0x20070000
            status,values=lookup(module);trace.append(('lookup',module,status))
            if status==0:
                assert len(values)==6
                for i,v in enumerate(values):word(memory,dest+4*i,v)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=status&MASK
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')
