# SPDX-License-Identifier: MIT
"""Restricted TWS tick execution versus independent event/call oracle."""
import json,re,subprocess,itertools
from build_gx8002_tws_tick_candidate import build,ROOT,IMAGE,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,bindings,available,module,kws,index,standby,locked,seed,helper_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x20070000;initial=r.copy();saved=None;pc=0x1836c;memory={0x2002e738:standby,0x20050008:index,0x2005000d:kws};events=[];condition=False
    reverse={v:k for k,v in bindings.items()}
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r15' and saved is None;saved=r['r15'];r['r14']-=4
        elif op=='pop':
            assert args=='r15' and r['r14']==0x2006fffc;r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return events
        elif op in ('movi','lrw','mov'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+b if op=='addi' else a-b)&MASK
        elif op in ('st.w','ld.w','ld.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op=='st.w':assert 0x2006ffec<=address<=0x2006fff8;memory[address]=r[reg]
            else:r[reg]=memory[address]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bez','bnez'):
            if (op=='bt' and condition) or (op=='bez' and r[p[0]]==0) or (op=='bnez' and r[p[0]]!=0):nxt=int(p[-1],0)
        elif op=='bsr':
            name=reverse[int(args,0)+0x1000dfec];a,b=r['r0'],r['r1'];value=0
            if name=='LvpQueueGet':
                assert (a,b)==(0x2002e6ec,0x2006ffec) and (memory[b],memory[b+4])==(0,0)
                if available:memory[b]=module;memory[b+4]=0x20050000
                value=available;events.append((name,))
            elif name=='LvpDoMaxDecoder':assert a==0x20050000;events.append((name,a))
            elif name=='LvpAudioInUpdateReadIndex':assert a==1;events.append((name,a))
            elif name=='LvpTriggerAppEvent':assert a==0x2006fff4;events.append((name,memory[a],memory[a+4]))
            elif name=='LvpPmuSuspendIsLocked':value=locked;events.append((name,))
            elif name=='LvpPmuSuspend':assert a==13;events.append((name,a))
            else:raise ValueError(name)
            if helper_hook is not None:
                override=helper_hook(name,memory)
                if override is not None:value=override
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
            r['r0']=value
        else:raise ValueError((op,args))
        pc=nxt
    raise ValueError('tick bound')

def verify():
    candidate=build();out=ROOT/'build/gx8002-board';wrapper=out/'padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');stock=IMAGE.read_bytes();assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-D','--start-address=0x1836c','--stop-address=0x183c8',str(wrapper)],text=True));cases=0
    # Builder proves source instructions are identical at the corresponding PCs.
    for args in itertools.product((0,1),(0,256,MASK),(0,1,255),(0,MASK),(2,4),(0,1),(0,91)):
        available,module,kws,index,standby,locked,seed=args;wanted=[('LvpQueueGet',)]
        if available:
            if module==256:wanted.extend([('LvpDoMaxDecoder',0x20050000),('LvpAudioInUpdateReadIndex',1)])
            if kws:wanted.append(('LvpTriggerAppEvent',kws,index))
        if standby==4:
            wanted.append(('LvpPmuSuspendIsLocked',))
            if not locked:wanted.append(('LvpPmuSuspend',13))
        assert execute(code,candidate['bindings'],*args)==wanted;cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Authenticated exact source/stock instruction equivalence transfers this decoded call oracle; void return intentionally unchecked. Helpers modeled with fixed context/state, no helper mutation or physical execution.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-tick-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
