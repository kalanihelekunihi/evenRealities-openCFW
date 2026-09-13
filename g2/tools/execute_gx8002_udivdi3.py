# SPDX-License-Identifier: MIT
import re,struct

def execute(code,entry,left,right,unpack_entry=None,pack_entry=None,multiply_entry=None,raw=False):
    """Execute finite multiply/divide instructions; nested unpack/pack use decoded bodies."""
    r={f'r{i}':0x70000000+i for i in range(32)};r['r14']=0x20050000
    operands=(left,right) if raw else tuple(struct.unpack('<Q',struct.pack('<d',x))[0] for x in (left,right))
    r['r0']=operands[0]&0xffffffff;r['r1']=operands[0]>>32
    r['r2']=operands[1]&0xffffffff;r['r3']=operands[1]>>32
    initial=r.copy();saved=[];condition=False;pc=entry
    memory={address:0xa5a5a5a5 for address in range(0x2004ff00,0x20050000,4)}
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
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Multiply ABI')
            return r['r0']|(r['r1']<<32)
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();address=r[base]+int(off,0)
            if not (0x2004ff00<=address<0x20050000):raise ValueError('Multiply memory bound')
            memory[address]=r[reg]
        elif op=='bsr':
            target=int(args,0);result=0
            if target in (unpack_entry,pack_entry):
                from execute_gx8002_unpack_double import execute as unpack
                from execute_gx8002_pack_double import execute as pack
                byte_memory={address+i:(value>>(8*i))&255 for address,value in memory.items() for i in range(4)}
                runner=unpack if target==unpack_entry else pack
                args=[r['r0'],r['r1']] if target==unpack_entry else [r['r0']]
                ret,after,events=runner(code,target,args,byte_memory,lambda *x:None)
                assert ret[0]=='return'
                for address in memory:memory[address]=sum(after[address+i]<<(8*i) for i in range(4))
                if target==pack_entry:result=ret[1]|(ret[2]<<32)
            elif target==multiply_entry:
                result=execute(code,target,r['r0']|(r['r1']<<32),r['r2']|(r['r3']<<32),raw=True)
            else:raise ValueError(('Multiply helper',hex(target)))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result&0xffffffff;r['r1']=result>>32
        elif op=='ff1':r[p[0]]=32-r[p[1]].bit_length()
        elif op=='divu':
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]]
            if not b:raise ZeroDivisionError('Target integer divide exception')
            r[p[0]]=a//b
        elif op=='ldr.b':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args)
            dest,base,index=m.groups();address=r[base]+r[index]
            if not 0x1020bd1c<=address<0x1020be1c:raise ValueError('CLZ table bounds')
            r[dest]=(address-0x1020bd1c).bit_length()
        elif op=='xor':r[p[0]]=r[p[1]]^r[p[2]] if len(p)==3 else r[p[0]]^r[p[1]]
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:following=int(p[1],0)
        elif op=='zexth':r[p[0]]=r[p[1]]&0xffff
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op in ('mult','mul.u32','mula.u32'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]]
            value=a*b;dest=int(p[0][1:])
            if op=='mula.u32':value+=r[p[0]]|(r[f'r{dest+1}']<<32)
            r[p[0]]=value&0xffffffff
            if op!='mult':r[f'r{dest+1}']=(value>>32)&0xffffffff
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
        elif op in ('bt','bf','br','bez','blz','blsz','bnez','bhsz'):
            take=condition if op=='bt' else not condition if op=='bf' else True if op=='br' else signed(r[p[0]])<=0 if op=='blsz' else r[p[0]]!=0 if op=='bnez' else r[p[0]]>=0x80000000 if op=='blz' else r[p[0]]<0x80000000 if op=='bhsz' else r[p[0]]==0
            if take:following=int(p[-1],0)
        else:raise ValueError('Multiply instruction '+op)
        pc=following
    raise ValueError('Multiply execution bound')
