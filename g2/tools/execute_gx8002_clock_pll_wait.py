# SPDX-License-Identifier: MIT
"""Decoded PLL wait execution with scripted observable helper/MMIO boundaries."""
import re
MASK=0xffffffff

def execute(code,entry,enable,timeout,after_enable,locks,times,time_runner=None,pll_runner=None,fields=None,registers=None,stock_delta=0x1000dfec,time_address=0x1002585c):
    r={f'r{i}':0x43210000+i for i in range(32)};r.update(r0=0x20030000,r1=timeout,r14=0x20070000)
    initial=r.copy();pc=entry;condition=False;saved=None;trace=[];li=ti=0
    mmio=dict(registers or {})
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args in ('r4, r15','r4-r8, r15');indices=(4,15) if args=='r4, r15' else (*range(4,9),15)
            saved={f'r{i}':r[f'r{i}'] for i in indices};r['r14']-=4*len(saved)
        elif op=='pop':
            r.update(saved);r['r14']+=4*len(saved);assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return 'return',r['r0'],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='rts':
            assert saved is None and all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return 'return',None,trace
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op in ('and','or'):r[p[0]]=r[p[0]]&r[p[1]] if op=='and' else r[p[0]]|r[p[1]]
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('cmpnei','cmpne','cmphs'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphs' else a!=b
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='mult':r[p[0]]=(r[p[0]]*r[p[1]])&MASK
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='sub.64':
            d,a,b=[int(v[1:]) for v in p];value=((r[f'r{a}']|(r[f'r{a+1}']<<32))-(r[f'r{b}']|(r[f'r{b+1}']<<32)))&((1<<64)-1)
            r[f'r{d}']=value&MASK;r[f'r{d+1}']=value>>32
        elif op in ('br','bt','bf','bez','bnez'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else (r[p[0]]==0)==(op=='bez')
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','ld.b','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(off,0)
            if fields is not None and 0x20030000<=a<0x20030038:
                assert op!='st.w';v=fields[(a-0x20030000)//4];r[reg]=v if op=='ld.w' else (v>>(8*((a-0x20030000)%4)))&255
                pc=nxt;continue
            elif fields is not None and a in mmio:
                if op=='st.w':mmio[a]=r[reg];trace.append(('write',a,r[reg]));pc=nxt;continue
                assert op=='ld.w';r[reg]=mmio[a]
            elif a==0x20030000:r[reg]=enable
            else:
                assert a==0xa0005098
                if li==len(locks):return 'poll',None,trace
                r[reg]=locks[li];li+=1
            trace.append(('read',a,r[reg]))
        elif op=='bsr':
            target=int(args,0)+(stock_delta if entry<0x100000 else 0)
            if target==0x10024b04:
                assert r['r0']==0x20030000;trace.append(('pll',r['r0']))
                if pll_runner is not None:trace.extend(pll_runner(enable))
                enable=after_enable;result=(0,0)
            else:
                assert target==time_address
                if ti==len(times):raise AssertionError('Missing scripted time')
                value=times[ti];ti+=1
                if time_runner is not None:value=time_runner(value)
                trace.append(('time',value));result=(value&MASK,value>>32)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0'],r['r1']=result
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')
