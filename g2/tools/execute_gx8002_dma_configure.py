# SPDX-License-Identifier: MIT
"""Bounded decoded descriptor builder with byte memory and abstract saved frame."""
import re
MASK=0xffffffff
def signed(v):return v if v<0x80000000 else v-0x100000000

def execute(code,entry,fields,length=80,channel=1,clear_hook=None,bus_hook=None,descriptor_hook=None):
    stack=0x20070000;config=0x20040000
    memory={a:0 for base,size in ((stack-96,100),(config,48),(0x2002e93c,900),(0xa1000000,256)) for a in range(base,base+size)}
    def put(a,v,n=4):
        for i in range(n):memory[a+i]=(v>>(8*i))&255
    def get(a,n=4):return sum(memory[a+i]<<(8*i) for i in range(n))
    for i,v in enumerate(fields):put(config+4*i,v)
    put(stack,config)
    put(0x2002e93c,0xa1000000)
    put(0x2002e93c+872+channel*4,0x20060000)
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=0x20050000,r1=0xa0000000,r2=length&MASK,r3=channel,r14=stack)
    initial=r.copy();saved=None;regs=[f'r{i}' for i in range(4,12)]+['r15','r16','r17'];condition=False;trace=[];pc=entry
    for _ in range(3000):
        op,args,step=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r11, r15, r16-r17' or saved is not None:raise ValueError('Descriptor frame')
            saved=[r[x] for x in regs];r['r14']-=44
        elif op=='pop':
            if args!='r4-r11, r15, r16-r17' or saved is None:raise ValueError('Descriptor restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=44
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Descriptor ABI')
            return r['r0'],trace
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addi','addu','subi','subu','lsli','lsl','mult','max.s32','or','ori','rotli'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else a<<b if op in ('lsli','lsl') else a*b if op=='mult' else a|b if op in ('or','ori') else ((a<<b)|(a>>(32-b))) if op=='rotli' else max(signed(a),signed(b)))&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='divs':
            a,b=signed(r[p[1]]),signed(r[p[2]]);r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&MASK
        elif op=='nor':r[p[0]]=(~r[p[1]])&MASK
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op in ('cmphs','cmphsi'):condition=r[p[0]]>=(r[p[1]] if p[1] in r else int(p[1],0))
        elif op in ('cmplt','cmplti','cmpnei','cmpne'):
            b=r[p[1]] if p[1] in r else int(p[1],0);condition=r[p[0]]!=b if op in ('cmpnei','cmpne') else signed(r[p[0]])<signed(b)
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('bt','bf','br','bnez','bez'):
            if op=='br' or (r[p[0]]!=0 if op=='bnez' else r[p[0]]==0 if op=='bez' else condition if op=='bt' else not condition):jump=int(p[-1],0)
        elif op.startswith(('ld.','ldr.','st.','str.')):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << [012])\)',args)
            if not m:raise ValueError('Descriptor operand '+args)
            reg,base,off=m.groups();offset=r[off.split()[0]]<<int(off[-1]) if '<<' in off else int(off,0);address=(r[base]+offset)&MASK
            size={'b':1,'h':2,'w':4}[op.split('.')[-1]]
            if any(address+i not in memory for i in range(size)):raise ValueError('Descriptor memory bounds')
            if op.startswith('st'):
                put(address,r[reg],size)
                if not stack-96<=address<stack:trace.append(('write',address,r[reg]))
            else:
                r[reg]=get(address,size)
                if not stack-96<=address<=stack:trace.append(('read',address,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            if entry==0xce80:target=(target+0x101f6a74)&MASK
            if target==0x10203804:
                trace.append(('clear',r['r0']));result=0xffffffff
                if clear_hook is not None:clear_hook(r['r0'])
            elif target==0x10203c60:
                addr=r['r0'];trace.append(('bus',addr));result=addr&0xfffffff if 0x10000000<=addr<0x30000000 else addr
                if bus_hook is not None:result=bus_hook(addr)
            elif target==0x10203828:
                ptr=r['r0'];event=('descriptors',r['r1'],r['r2'],r['r3'],get(r['r14'],1),get(ptr),get(ptr+4),get(ptr+12));trace.append(event);result=0xffffffff
                if descriptor_hook is not None:descriptor_hook(*event[1:])
            else:raise ValueError('Configuration helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=result
        else:raise ValueError('Descriptor instruction '+op)
        pc=jump if jump is not None else pc+step
    raise ValueError('Descriptor instruction bound')
