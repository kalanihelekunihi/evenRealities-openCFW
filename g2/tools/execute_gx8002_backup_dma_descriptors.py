# SPDX-License-Identifier: MIT
"""Bounded decoded descriptor builder with byte memory and abstract saved frame."""
import re
MASK=0xffffffff
def signed(v):return v if v<0x80000000 else v-0x100000000

def execute(code,entry,count,length,control,width,bus_hook=None,source_address=0xfffffff0,destination_address=0x20000000,output_address=0x20050000,bus_address=None):
    stack=0x20070000;pattern=0x20040000;output=output_address
    memory={a:0xa5 for base,size in ((stack-96,100),(pattern,24),(output,432)) for a in range(base,base+size)}
    def put(a,v,n=4):
        for i in range(n):memory[a+i]=(v>>(8*i))&255
    def get(a,n=4):return sum(memory[a+i]<<(8*i) for i in range(n))
    for i,v in enumerate((source_address,destination_address,0xdeadbeef,control,0x12345678,0xaabbccdd)):put(pattern+4*i,v)
    put(stack,width)
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=pattern,r1=output,r2=count,r3=length&MASK,r14=stack)
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
            return bytes(memory[output+i] for i in range(432)),trace
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addi','addu','subi','subu','lsli','mult','max.s32'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else a<<b if op=='lsli' else a*b if op=='mult' else max(signed(a),signed(b)))&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='divs':
            a,b=signed(r[p[1]]),signed(r[p[2]]);r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&MASK
        elif op=='nor':r[p[0]]=(~r[p[1]])&MASK
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op in ('cmplt','cmplti','cmpnei','cmpne'):
            b=r[p[1]] if p[1] in r else int(p[1],0);condition=r[p[0]]!=b if op in ('cmpnei','cmpne') else signed(r[p[0]])<signed(b)
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('bt','bf','br','bnez','bez'):
            if op=='br' or (r[p[0]]!=0 if op=='bnez' else r[p[0]]==0 if op=='bez' else not condition if op=='bf' else condition):jump=int(p[-1],0)
        elif op.startswith(('ld.','ldr.','st.')):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << [012])\)',args)
            if not m:raise ValueError('Descriptor operand '+args)
            reg,base,off=m.groups();offset=r[off.split()[0]]<<int(off[-1]) if '<<' in off else int(off,0);address=(r[base]+offset)&MASK
            size={'b':1,'h':2,'w':4}[op.split('.')[-1]]
            if any(address+i not in memory for i in range(size)):raise ValueError('Descriptor memory bounds')
            if op.startswith('st'):
                put(address,r[reg],size)
                if output<=address<output+432:trace.append(('write',address,r[reg]&((1<<(size*8))-1)))
            else:
                r[reg]=get(address,size)
                if pattern<=address<pattern+24:trace.append(('read',address,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            targets=(0xd1ec,0x10203c60) if bus_address is None else (bus_address,)
            if target not in targets:raise ValueError('Descriptor helper')
            address=r['r0'];trace.append(('bus',address));result=address&0xfffffff if 0x10000000<=address<0x30000000 else address
            if bus_hook is not None:result=bus_hook(address)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=result
        else:raise ValueError('Descriptor instruction '+op)
        pc=jump if jump is not None else pc+step
    raise ValueError('Descriptor instruction bound')
