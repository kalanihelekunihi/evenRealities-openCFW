# SPDX-License-Identifier: MIT
"""Decoded initializer with explicit modeled helper/callback boundaries."""
import re
STACK=0x20070000
STATE=0x20027330

def execute(code,entry,callbacks,seed,input_mask,output_mask,selector,reset_hook=None,config_hook=None):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update({f'r{i}':callbacks[i] for i in range(4)});r['r14']=STACK;initial=r.copy()
    stack={STACK:callbacks[4]};memory={STATE+4*i:seed for i in range(7)}
    memory.update({0xa0a00000+off:seed for off in (0,4,12,0x28,0x2c,0x48,0x4c,0x100,0x10c)})
    for off in (0x28,0x2c,0x48,0x4c):memory[0xa0a00000+off]=(seed&~15)|selector
    trace=[];pc=entry;condition=False
    for _ in range(400):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r9, r15':raise ValueError('Initializer saved frame')
            r['r14']-=28
            for i,name in enumerate((*[f'r{j}' for j in range(4,10)],'r15')):stack[r['r14']+i*4]=r[name]
        elif op=='ldm':
            if args!='r4-r9, (r14)':raise ValueError('Initializer restore frame')
            for i in range(6):r[f'r{i+4}']=stack[r['r14']+i*4]
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)) or stack[STACK]!=callbacks[4]:raise ValueError('Initializer ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','movih','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi','andi','andni','ori'):
            a=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0)
            r[p[0]]={'addi':lambda:a+n,'subi':lambda:a-n,'andi':lambda:a&n,'andni':lambda:a&~n,'ori':lambda:a|n}[op]()&0xffffffff
        elif op in ('bseti','bclri'):
            bit=1<<int(p[-1],0);r[p[0]]=r[p[0]]|bit if op=='bseti' else r[p[0]]&~bit
        elif op=='cmplti':condition=(r[p[0]] if r[p[0]]<0x80000000 else r[p[0]]-0x100000000)<int(p[1],0)
        elif op=='bf':
            if not condition:jump=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Initializer operand')
            reg,base,off=m.groups();a=(r[base]+int(off,0))&0xffffffff
            if STACK-44<=a<=STACK and a%4==0:
                if op=='ld.w':r[reg]=stack[a]
                else:stack[a]=r[reg]
            elif a in memory:
                if op=='ld.w':r[reg]=memory[a];trace.append(('read',a,r[reg]))
                else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
            else:raise ValueError('Initializer access '+hex(a))
        elif op in ('bsr','jsr'):
            target=r[args] if op=='jsr' else (int(args,0)+(0x101f6a74 if entry==0xdd70 else 0))&0xffffffff
            if op=='jsr':
                if target!=callbacks[1] or not target:raise ValueError('Initializer callback target')
                trace.append(('config',target));memory[STATE]=input_mask;memory[STATE+4]=output_mask
                if config_hook is not None:
                    nested,new_state=config_hook(memory.copy())
                    trace.extend(tuple(item) for item in nested);memory.update(new_state)
            elif target==0x10025080:trace.append(('gate',r['r0'],r['r1']))
            elif target==0x102099cc:
                if (r['r0'],r['r1'],r['r2'])!=(STATE,0,28):raise ValueError('Initializer memset args')
                trace.append(('memset',STATE,0,28))
                for i in range(7):memory[STATE+4*i]=0
            elif target==0x10203c88:
                trace.append(('reset',))
                if reset_hook is not None:
                    nested,new_state=reset_hook(memory.copy())
                    trace.extend(tuple(item) for item in nested);memory.update(new_state)
            elif target==0x1002553c:trace.append(('irq',r['r0'],r['r1'],r['r2']))
            else:raise ValueError('Initializer helper '+hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=0xffffffff
        else:raise ValueError('Initializer instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Initializer bound')
