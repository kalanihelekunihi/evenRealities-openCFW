# SPDX-License-Identifier: MIT
"""Scoped decoded UART interrupt execution; callback bodies modeled."""
import re


def execute(code,entry,descriptor,registers,callback_hook=None,read_hook=None,poll_limit=None,descriptor_base=0x20026a94):
    base=descriptor_base
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=6,r1=base,r14=0x20050000)
    initial=r.copy();saved=None;memory={base+4*i:v for i,v in enumerate(descriptor)};memory.update(registers)
    trace=[];pc=entry;condition=False;poll_reads=0
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(3000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('UART interrupt frame')
            saved={f'r{i}':r[f'r{i}'] for i in (4,5,15)};r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('UART interrupt restore')
            r.update(saved);r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('UART interrupt ABI')
            return r['r0'],memory,trace
        elif op in ('ld.w','ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,source,off=m.groups();address=(r[source]+int(off,0))&0xffffffff
            if address&~3 not in memory:raise ValueError(('UART memory address',hex(address)))
            if op=='st.w':
                if address&3:raise ValueError('Unaligned UART store')
                memory[address]=r[reg];trace.append(('write',address,4,r[reg]))
            else:
                value=memory[address&~3]
                if read_hook is not None:value=read_hook(address,value)
                if poll_limit is not None and address in (0xa0100014,0xa0200014):
                    poll_reads+=1
                    if poll_reads==poll_limit:
                        trace.append(('read',address,4,value))
                        return None,memory,trace
                if op=='ld.b':value=(value>>((address&3)*8))&255
                r[reg]=value;trace.append(('read',address,1 if op=='ld.b' else 4,value))
        elif op in ('stbi.b','ldbi.b','str.b','ldr.b'):
            if op in ('stbi.b','ldbi.b'):
                m=re.fullmatch(r'(r\d+), \((r\d+)\)',args);reg,source=m.groups();address=r[source];r[source]=(address+1)&0xffffffff
            else:
                m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args);reg,a,b=m.groups();address=(r[a]+r[b])&0xffffffff
            if address&~3 not in memory:raise ValueError('UART byte bounds')
            shift=(address&3)*8
            if op in ('stbi.b','str.b'):
                value=r[reg]&255;memory[address&~3]=(memory[address&~3]&~(255<<shift))|(value<<shift);trace.append(('write',address,1,value))
            else:
                r[reg]=(memory[address&~3]>>shift)&255;trace.append(('read',address,1,r[reg]))
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op in ('addi','addu','subi','subu','lsli','lsri','asri','andi','and','ori','andni','mult','divu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            value=a+b if op in ('addi','addu') else a-b if op in ('subi','subu') else a<<b if op=='lsli' else a>>b if op=='lsri' else signed(a)>>b if op=='asri' else a&b if op in ('andi','and') else a|b if op=='ori' else a&~b if op=='andni' else a*b if op=='mult' else a//b
            r[p[0]]=value&0xffffffff
        elif op=='btsti':condition=bool(r[p[0]]&(1<<int(p[1],0)))
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op in ('cmpnei','cmphsi'):
            condition=r[p[0]]!=int(p[1],0) if op=='cmpnei' else r[p[0]]>=int(p[1],0)
        elif op in ('br','bt','bf','bez','bnez','bhsz'):
            take=True if op=='br' else condition if op=='bt' else not condition if op=='bf' else r[p[0]]==0 if op=='bez' else r[p[0]]!=0 if op=='bnez' else signed(r[p[0]])>=0
            if take:following=int(p[-1],0)
        elif op=='jsr':
            target=r[p[0]]
            count=3 if target in (0x10300000,0x10300010) else 2
            trace.append(('callback',target,*(r[f'r{i}'] for i in range(count))))
            if callback_hook is not None:callback_hook(target,memory)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        else:raise ValueError(('UART interrupt opcode',hex(pc),op,args))
        pc=following
    raise ValueError('UART interrupt execution bound')
