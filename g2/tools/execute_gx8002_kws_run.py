# SPDX-License-Identifier: MIT
"""Restricted runner instruction execution with modeled helper boundaries."""
import re
MASK=0xffffffff

def execute(code,entry,bindings,context,index,stride,features,output,dimension,seed,memory_hook=None,cache_hook=None,model_hook=None,task_hook=None,context_hook=None,submit_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r.update(r0=context,r14=0x20070000);initial=r.copy();saved=None;pc=entry;events=[];memory={context+8:index,context+16:0x20050000,0x20051010:0x20052000,0x20053010:0x20054000};lookups=0
    names={v:k for k,v in bindings.items()}
    for _ in range(150):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            regs=tuple(f'r{i}' for i in range(4,11 if entry==0x180f8 else 10))+('r15',)
            assert saved is None and args==('r4-r10, r15' if entry==0x180f8 else 'r4-r9, r15');saved={n:r[n] for n in regs};r['r14']-=len(regs)*4
        elif op in ('pop','rts'):
            if op=='pop':
                assert saved and r['r14']==initial['r14']-len(saved)*4;r.update(saved);r['r14']=initial['r14']
            else:assert saved is None
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return r['r0'],events
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b)&MASK
        elif op in ('addu','subu','mult'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+b if op=='addu' else a-b if op=='subu' else a*b)&MASK
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op in ('bez','br'):
            if op=='br' or r[p[0]]==0:nxt=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=memory[address]
            else:assert r['r14']<=address<r['r14']+44;memory[address]=r[reg]
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry==0x180f8 else 0);name=names[target];a,b,c=[r[f'r{i}'] for i in range(3)];value=0;sp=r['r14']
            if name=='LvpGetFeatsBuffer':value=0x20040000;events.append((name,))
            elif name=='LvpGetLogfbankBuffer':assert (a,b)==(context,index);value=0x20041000;events.append((name,a,b))
            elif name=='LvpGetPcmFrameNumPerContext':value=stride;events.append((name,))
            elif name in ('gx_dcache_invalid_range','gx_dcache_clean_range'):
                events.append((name,a,b))
                if cache_hook:cache_hook(name,a,b)
            elif name in ('memcpy','memmove'):
                events.append((name,a,b,c));value=a if memory_hook is None else memory_hook(name,a,b,c)
            elif name=='LvpGetContext':
                assert b==sp+4*lookups and c==sp+8;assert a==(index+lookups)&MASK
                if context_hook:context_hook(a,b,c,memory)
                else:memory[b]=0x20051000 if lookups==0 else 0x20053000;memory[c]=32
                lookups+=1;events.append((name,a))
            elif name=='LvpCTCModelInitSnpuTask':
                assert a==sp+12
                for i in range(8):memory[a+4*i]=(seed+i)&MASK
                if task_hook:task_hook(a,memory)
                events.append((name,))
            elif name=='LvpCTCModelGetSnpuFeatsBuffer':assert a==memory[memory[sp]+16];value=features if model_hook is None else model_hook(name,a);events.append((name,a))
            elif name=='LvpCTCModelGetSnpuStateBuffer':assert a==memory[memory[sp+4]+16];value=output if model_hook is None else model_hook(name,a);events.append((name,a))
            elif name=='LvpCTCModelGetSnpuFeatsDim':value=dimension if model_hook is None else model_hook(name,a);events.append((name,))
            elif name=='gx_snpu_run_task':
                assert a==sp+12 and b==0x100260d0 and c==memory[sp+4]
                events.append((name,tuple(memory[a+i*4] for i in range(8)),b,c))
                if submit_hook:value=submit_hook(a,b,c,memory)
            else:raise ValueError(name)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xbad00000+i)&MASK
            r['r0']=value&MASK
        else:raise ValueError((op,args))
        pc=nxt
    raise ValueError('runner execution bound')
