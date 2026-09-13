# SPDX-License-Identifier: MIT
"""Decoded application reply with preserved register checks."""
import re
MASK=0xffffffff

def execute(code,entry,arguments,memory,helper):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;r.update({f'r{i}':v for i,v in enumerate(arguments[:4])});initial=r.copy();saved=None;events=[];pc=entry;condition=False
    frame='r15'
    regs=('r15',)
    stack=r['r14']-4*len(regs)-28
    stack_end=r['r14']-4*len(regs)
    memory.update({i:0xa5 for i in range(stack,stack_end)})
    for _ in range(2000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!=frame or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in regs};r['r14']-=4*len(regs)
        elif op in ('pop','rts'):
            if op=='pop':
                if args!=frame or saved is None:raise ValueError('Restore')
                r.update(saved);r['r14']+=4*len(regs)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return ('return',r['r0']),{k:v for k,v in memory.items() if not stack<=k<stack_end},events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='btsti':condition=bool(r[p[0]]&(1<<int(p[1],0)))
        elif op in ('blz','bhsz'):
            if (r[p[0]]>=0x80000000)==(op=='blz'):nxt=int(p[1],0)
        elif op in ('lsl','lsr'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]]
            r[p[0]]=(0 if b>=32 else a<<b if op=='lsl' else a>>b)&MASK
        elif op=='divu':
            if not r[p[2]]:return ('divide_exception',),{k:v for k,v in memory.items() if not stack<=k<stack_end},events
            r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='mult':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]*r[p[-1]])&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('addu','subu','lsli','lsri','or'):
            left=r[p[0] if len(p)==2 else p[1]];right=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(left+right if op=='addu' else left-right if op=='subu' else left<<right if op=='lsli' else left>>right if op=='lsri' else left|right)&MASK
        elif op=='cmplti':condition=(r[p[0]] if r[p[0]]<0x80000000 else r[p[0]]-0x100000000)<int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='and':r[p[0]]=r[p[0] if len(p)==2 else p[1]]&r[p[-1]]
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='andni':r[p[0]]=r[p[1]]&(~int(p[2],0)&MASK)
        elif op=='incf':
            if not condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('ld.w','st.w','ld.b','st.b','st.h','ld.h','ldr.w','str.w','ldr.b','str.b'):
            if op in ('ldr.w','str.w','ldr.b','str.b'):
                reg,base,index,shift=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args).groups();address=(r[base]+(r[index]<<int(shift)))&MASK
            else:
                reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(off,0))&MASK
            if op.startswith('ld'):
                r[reg]=sum(memory[address+i]<<(8*i) for i in range(1 if op in ('ld.b','ldr.b') else 2 if op=='ld.h' else 4))
            else:
                size=1 if op in ('st.b','str.b') else 2 if op=='st.h' else 4
                if any(address+i not in memory for i in range(size)):raise ValueError('Out of bounds write')
                for i in range(size):memory[address+i]=(r[reg]>>(8*i))&255
                if not stack<=address<stack_end:
                    events.extend(('write_byte',address+i,memory[address+i]) for i in range(size))
        elif op=='ldbi.b':
            reg,base=re.fullmatch(r'(r\d+), \((r\d+)\)',args).groups();r[reg]=memory[r[base]];r[base]=(r[base]+1)&MASK
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('bsr','jsr'):
            target=r[args] if op=='jsr' else (int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&MASK
            value=helper(target,[r['r'+str(i)] for i in range(4)],memory,events)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError(('Opcode',op))
        pc=nxt
    return ('bounded_loop',),{k:v for k,v in memory.items() if not stack<=k<stack_end},events
