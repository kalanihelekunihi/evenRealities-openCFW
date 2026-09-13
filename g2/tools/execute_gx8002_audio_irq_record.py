# SPDX-License-Identifier: MIT
"""Shared-memory adaptation of the qualified restricted audio-record executor.
No context or SDC allocation/reset here: caller supplies live byte RAM and SP.
"""
import re
from verify_gx8002_power_initialize import word
MASK=0xffffffff
HEADER=0x20027b60
def execute(code,entry,bindings,channel,memory,SDC,stack_pointer,vad,seed,record_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=channel,r1=SDC,r14=stack_pointer);initial=r.copy();saved=None;pc=entry;condition=False;events=[]
    names={v:k for k,v in bindings.items()}
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r11, r15, r16-r17' and saved is None
            saved={f'r{i}':r[f'r{i}'] for i in (*range(4,12),15,16,17)};r['r14']-=44
        elif op=='pop':
            assert r['r14']==initial['r14']-44;r.update(saved);r['r14']+=44
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],events
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','subu','mult','lsli','andi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else a*b if op=='mult' else a<<b if op=='lsli' else a&b)&MASK
        elif op in ('divu','divs'):
            a,b=r[p[1]],r[p[2]]
            if op=='divs':a,b=signed(a),signed(b)
            assert b;r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&MASK
        elif op=='ins':
            hi,lo=map(int,p[2:]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w','ld.b','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=word(memory,a)
            elif op=='ld.b':r[reg]=memory[a]
            elif op=='st.w':word(memory,a,r[reg])
            else:memory[a]=r[reg]&255
        elif op in ('cmphs','cmpne','cmplti'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0);condition=a>=b if op=='cmphs' else a!=b if op=='cmpne' else signed(a)<b
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('br','bt','bf','bez','bnez'):
            take=op=='br' or op=='bt' and condition or op=='bf' and not condition or op=='bez' and r[p[0]]==0 or op=='bnez' and r[p[0]]!=0
            if take:nxt=int(p[-1],0)
        elif op in ('bsr','jsr'):
            if op=='jsr':
                assert r[p[0]]==0x10210000 and r['r1']==SDC+8
                events.append(('record',r['r0'],r['r1']));value=seed
                if record_hook:value=record_hook(memory,r['r0'],r['r1'])
            else:
                target=int(args,0)+(0x1000dfec if entry==0x18228 else 0);name=names[target];events.append((name,))
                if name=='LvpAudioInQueryFFTVad':assert r['r0']==SDC+8;value=vad
                else:value={'LvpGetContextHeader':HEADER,'LvpGetLogfbankFrameNumPerChannel':13,'LvpGetPcmFrameNumPerContext':1,'LvpGetContextNum':3,'LvpGetContextGap':1}[name]
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
            r['r0']=value&MASK
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('audio record execution bound')
