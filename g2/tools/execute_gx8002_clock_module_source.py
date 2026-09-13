# SPDX-License-Identifier: MIT
import re
from verify_gx8002_power_initialize import word
MASK=0xffffffff
def execute(code,entry,module,source,table,modules,registers,lookup_runner=None,register_runner=None):
    r={f'r{i}':0x43210000+i for i in range(32)};r.update(r0=module,r1=source,r14=0x20070000);initial=r.copy();saved=None;pc=entry;condition=False;calls=[];memory=dict(table);mmio=dict(registers);trace=[]
    def rd(a):
        trace.append(("read",a,mmio[a]));return mmio[a]
    def wr(a,v):
        mmio[a]=v;trace.append(("write",a,v))
        if a&255 in (0x1c,0x20):
            normal=(a&~255)+0x18
            mmio[normal]=(mmio[normal]|v) if a&255==0x1c else (mmio[normal]&~v)&MASK
    def signed(v):return v if v<0x80000000 else v-(1<<32)
    for _ in range(200):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            end=int(re.fullmatch(r'r4-r(\d+), r15',args)[1]);regs=[f'r{i}' for i in range(4,end+1)]+['r15'];saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            r.update(saved);r['r14']+=4*len(saved);assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],calls,trace,mmio
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('cmphs','cmphsi','cmpnei','cmpne','cmplti'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0)
            condition=a>=b if op.startswith('cmphs') else a!=b if op in ('cmpnei','cmpne') else signed(a)<b
        elif op in ('lsl','lsr','asri','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);assert b<32
            r[p[0]]=((a<<b) if op in ('lsl','lsli') else (a>>b) if op=='lsr' else (signed(a)>>b))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('br','bt','bf','bez','bnez'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op in ('addu','and','or','nor'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]]
            r[p[0]]=(a+b if op=='addu' else a&b if op=='and' else a|b if op=='or' else ~(a|b))&MASK
        elif op=='sextb':
            v=r[p[1]]&255;r[p[0]]=(v if v<128 else v-256)&MASK
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op in ('st.w','ld.w','ld.b','ld.bs'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if op=='st.w':
                if a in mmio:wr(a,r[reg])
                else:
                    assert 0x2006ff80<=a<0x20070000;word(memory,a,r[reg])
            elif a in mmio:
                assert op=='ld.w';r[reg]=rd(a)
            elif op=='ld.w':r[reg]=word(memory,a)
            else:
                v=memory[a];r[reg]=(v if op=='ld.b' or v<128 else v-256)&MASK
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0)
            if target==0x10024a44:
                assert r['r0']==module;dest=r['r1'];calls.append(('lookup',module));base=0xa0010000 if module<10 else 0xa0300000
                vals=(modules[module]['address'],base,base+(0x8c if module<10 else 0x88),base+0x18,base+0x1c,base+0x20)
                if lookup_runner is not None:
                    actual=lookup_runner(module);assert tuple(actual)==vals;vals=actual
                assert 0x2006ff80<=dest and dest+24<=0x20070000
                for i,v in enumerate(vals):word(memory,dest+4*i,v)
            else:
                assert target==0x10024a30
                address,offset,value,mask=[r[f'r{i}'] for i in range(4)];assert offset<32
                calls.append(('set',address,offset,value,mask));prior=rd(address)
                updated=(prior&~((mask<<offset)&MASK))|((value<<offset)&MASK)
                if register_runner is not None:
                    actual=register_runner(address,offset,value,mask,prior);assert actual==updated;updated=actual
                wr(address,updated)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=0
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')