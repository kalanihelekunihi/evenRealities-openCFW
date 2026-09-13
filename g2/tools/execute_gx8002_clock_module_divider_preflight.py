# SPDX-License-Identifier: MIT
"""Decoded divider early-exit executor; stops at the current-divider helper."""
import re
from verify_gx8002_power_initialize import word
MASK=0xffffffff

def execute(code,entry,module,divider,table,lookup):
    r={f'r{i}':0x43210000+i for i in range(32)};r.update(r0=module,r1=divider,r14=0x20070000)
    initial=r.copy();memory=dict(table);pc=entry;condition=False;saved=None;trace=[]
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r11, r15, r16-r17';saved={f'r{i}':r[f'r{i}'] for i in (*range(4,12),15,16,17)};r['r14']-=4*len(saved)
        elif op=='pop':
            assert args=='r4-r11, r15, r16-r17';r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert all(memory[a]==v for a,v in table.items())
            return 'return',trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('cmphsi','cmpnei','cmpne'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphsi' else a!=b
        elif op in ('lsl','lsr'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];assert b<32;r[p[0]]=((a<<b) if op=='lsl' else a>>b)&MASK
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('br','bt','bf','bez','bnez'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','ld.bs','ld.b','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if op=='st.w':
                assert 0x2006ff80<=a<0x20070000;word(memory,a,r[reg])
            elif op=='ld.w':r[reg]=word(memory,a)
            else:
                v=memory[a];r[reg]=(v if op=='ld.b' or v<128 else v-256)&MASK
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0)
            if target==0x10024ae8:
                status,values=lookup(module);assert status==0
                assert (r['r0'],r['r1'])==tuple(values[:2])
                assert all(memory[a]==v for a,v in table.items())
                return 'divider',trace
            assert target==0x10024a44
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
