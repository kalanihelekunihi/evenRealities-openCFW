# SPDX-License-Identifier: MIT
import re

def execute(code,entry,left,right,full=False):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=0x20040000,r1=0x20040100,r2=0x20040200,r14=0x20050000)
    initial=r.copy();saved=[];condition=False;pc=entry
    memory={base+off:value for base,fields in ((0x20040000,left),(0x20040100,right),(0x20040200,{off:0xa5a5a5a5 for off in (0,4,8,12,16)})) for off,value in {**{k:0xa5a5a5a5 for k in (0,4,8,12,16)},**fields}.items()}
    memory.update({0x1020bd08+off:0 for off in (0,4,8,12,16)})
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            regs=[]
            for part in p:
                if '-' in part:
                    lo,hi=part.split('-');regs.extend('r'+str(i) for i in range(int(lo[1:]),int(hi[1:])+1))
                else:regs.append(part)
            saved.append((regs,[r[k] for k in regs]));r['r14']-=4*len(regs)
        elif op in ('pop','rts'):
            if op=='pop':
                regs,values=saved.pop()
                for k,v in zip(regs,values):r[k]=v
                r['r14']+=4*len(regs)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Add core ABI')
            if full:return r['r0'],{k:v for k,v in memory.items() if not 0x2004ff00<=k<0x20050000}
            return r['r0'],{off:memory[r['r0']+off] for off in (0,4,8,12,16)}
        elif op in ('stbi.w','ldbi.w'):
            reg,base=re.fullmatch(r'(r\d+), \((r\d+)\)',args).groups();address=r[base]
            if op=='stbi.w':
                if address not in memory:raise ValueError('Postincrement bound')
                memory[address]=r[reg]
            else:r[reg]=memory[address]
            r[base]=(address+4)&0xffffffff
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=r[base]+int(off,0)
            if not (0x20040000<=address<0x20040314 or 0x2004ff00<=address<0x20050000):raise ValueError('Add memory bound')
            memory[address]=r[reg]
        elif op=='abs':r[p[0]]=abs(signed(r[p[1]]))
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();r[reg]=memory[r[base]+int(off,0)]
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op in ('zext','ins'):
            hi,lo=map(int,p[2:]);mask=(1<<(hi-lo+1))-1
            if op=='zext':r[p[0]]=(r[p[1]]>>lo)&mask
            else:r[p[0]]=(r[p[0]]&~(mask<<lo))|((r[p[1]]&mask)<<lo)
        elif op in ('or','nor','and','andi','addi','addu','subi','subu','lsl','lsr','lsli','lsri','addc','subc'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            value=a|b if op=='or' else ~(a|b) if op=='nor' else a&b if op in ('and','andi') else a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else (0 if b>=32 else a<<b) if op in ('lsl','lsli') else (0 if b>=32 else a>>b) if op in ('lsr','lsri') else a-b-(1-int(condition)) if op=='subc' else a+b+int(condition)
            if op in ('addc','subc'):condition=value>=0 if op=='subc' else value>0xffffffff
            r[p[0]]=value&0xffffffff
        elif op=='btsti':condition=bool(r[p[0]]&(1<<int(p[1],0)))
        elif op=='mvc':r[p[0]]=int(condition)
        elif op in ('inct','incf','decf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+(-1 if op=='decf' else 1)*int(p[2],0))&0xffffffff
        elif op in ('add.64','sub.64'):
            dest,a,b=[int(x[1:]) for x in p];value=(r[f'r{a}']|(r[f'r{a+1}']<<32))+(1 if op=='add.64' else -1)*(r[f'r{b}']|(r[f'r{b+1}']<<32))
            r[f'r{dest}']=value&0xffffffff;r[f'r{dest+1}']=(value>>32)&0xffffffff
        elif op in ('cmphsi','cmphs','cmpnei','cmpne','cmplti','cmplt'):
            a=r[p[0]];b=r[p[1]] if p[1] in r else int(p[1],0)
            condition=a>=b if op in ('cmphsi','cmphs') else a!=b if op in ('cmpnei','cmpne') else signed(a)<signed(b)
        elif op in ('bt','bf','br','bez','blz','blsz','bnez'):
            take=condition if op=='bt' else not condition if op=='bf' else True if op=='br' else signed(r[p[0]])<=0 if op=='blsz' else r[p[0]]!=0 if op=='bnez' else r[p[0]]>=0x80000000 if op=='blz' else r[p[0]]==0
            if take:following=int(p[-1],0)
        else:raise ValueError('Pack instruction '+op)
        pc=following
    raise ValueError('Pack execution bound')
