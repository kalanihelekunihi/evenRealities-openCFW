# SPDX-License-Identifier: MIT
"""Complete decoded divider programming with explicit helper boundaries."""
import re
from verify_gx8002_power_initialize import word
MASK=0xffffffff

def execute(code,entry,module,divider,table,lookup,registers,divider_runner=None,register_runner=None):
    r={f'r{i}':0x43210000+i for i in range(32)};r.update(r0=module,r1=divider,r14=0x20070000)
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
            assert args=='r4-r11, r15, r16-r17';saved={f'r{i}':r[f'r{i}'] for i in (*range(4,12),15,16,17)};r['r14']-=4*len(saved)
        elif op=='pop':
            assert args=='r4-r11, r15, r16-r17';r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            assert all(memory[a]==v for a,v in table.items())
            return trace,mmio
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
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
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0)
            if target==0x10024ae8:
                status,values=lookup(module);assert status==0
                assert (r['r0'],r['r1'])==tuple(values[:2])
                ptr=word(table,values[0]+8);offset=table[ptr];shift=table[ptr+1];mask=table[ptr+2]|table[ptr+3]<<8
                prior=rd(values[1]+offset);current=(prior>>shift)&mask;status=current+1 if current else 0
                if divider_runner is not None:assert divider_runner(values[1],offset,shift,mask,prior)==status
                trace.append(('divider',status))
            elif target==0x10024a30:
                address,offset,value,mask=[r[f'r{i}'] for i in range(4)];assert offset<32
                trace.append(('set',address,offset,value,mask));prior=rd(address);updated=((prior&~(mask<<offset))|(value<<offset))&MASK
                if register_runner is not None:assert register_runner(address,offset,value,mask,prior)==updated
                wr(address,updated);status=0
            else:
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
