# SPDX-License-Identifier: MIT
"""Complete decoded DTO programming with explicit helper boundaries."""
import re
from verify_gx8002_power_initialize import word
MASK=0xffffffff

def execute(code,entry,module,dto,enable,table,lookup,registers,register_runner=None,stock_delta=0x1000dfec,lookup_address=0x10024a44):
    r={f'r{i}':0x43210000+i for i in range(32)};r.update(r0=module,r1=dto,r2=enable,r14=0x20070000)
    initial=r.copy();memory=dict(table);pc=entry;condition=False;saved=None;trace=[];mmio=dict(registers)
    def rd(a):
        trace.append(('read',a,mmio[a]));return mmio[a]
    def wr(a,v):
        mmio[a]=v;trace.append(('write',a,v))
        if a&255 in (0x1c,0x20):
            normal=(a&~255)+0x18
            mmio[normal]=(mmio[normal]|v) if a&255==0x1c else mmio[normal]&~v&MASK
    for _ in range(300):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            regs=[]
            for part in p:
                if '-' in part:
                    first,last=part.split('-');regs.extend(f'r{i}' for i in range(int(first[1:]),int(last[1:])+1))
                else:regs.append(part)
            saved={k:r[k] for k in regs};r['r14']-=4*len(saved)
        elif op=='pop':
            r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert all(memory[a]==v for a,v in table.items())
            return trace,mmio
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='rotl':
            a=r[p[1] if len(p)==3 else p[0]];n=r[p[-1]]&31;r[p[0]]=((a<<n)|(a>>(32-n)))&MASK
        elif op=='movih':r[p[0]]=int(p[1],0)<<16
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('cmphs','cmphsi','cmpnei','cmpne'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op in ('cmphs','cmphsi') else a!=b
        elif op in ('lsl','lsr','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);assert b<32;r[p[0]]=((a<<b) if op in ('lsl','lsli') else a>>b)&MASK
        elif op in ('addu','andn','or','nor','and'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+b if op=='addu' else a&~b if op=='andn' else ~(a|b) if op=='nor' else a&b if op=='and' else a|b)&MASK
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='xor':r[p[0]]^=r[p[1]]
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op=='bseti':r[p[0]]=(r[p[1]] if len(p)==3 else r[p[0]])|(1<<int(p[-1],0))
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('br','bt','bf','bez','bnez','blz'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else r[p[0]]>=0x80000000 if op=='blz' else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','ld.bs','ld.b','ld.h','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if op=='st.w':
                if a in mmio:wr(a,r[reg])
                else:
                    assert 0x2006ff80<=a<0x20070000;word(memory,a,r[reg])
            elif a in mmio:
                assert op=='ld.w';r[reg]=rd(a)
            elif op=='ld.h':r[reg]=memory[a]|memory[a+1]<<8
            elif op=='ld.w':r[reg]=word(memory,a)
            else:
                v=memory[a];r[reg]=(v if op=='ld.b' or v<128 else v-256)&MASK
        elif op=='bsr':
            target=int(args,0)+(stock_delta if entry<0x100000 else 0)
            if target==0x10024a30:
                address,offset,value,mask=[r[f'r{i}'] for i in range(4)];assert offset<32
                trace.append(('set',address,offset,value,mask));prior=rd(address);updated=((prior&~(mask<<offset))|(value<<offset))&MASK
                if register_runner is not None:assert register_runner(address,offset,value,mask,prior)==updated
                wr(address,updated);status=0
            else:
                assert target==lookup_address
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
