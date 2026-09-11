# SPDX-License-Identifier: MIT
"""Scoped decoded UART configuration execution with explicit helper boundaries."""
import re


def execute(code,entry,descriptor,registers,helpers,arithmetic,depth,changed_device=None,fifo_hook=None,irq_hook=None,descriptor_base=0x20026a94):
    base=descriptor_base
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=base,r14=0x20050000)
    initial=r.copy();saved=None;memory={base+4*i:v for i,v in enumerate(descriptor)};memory.update(registers)
    trace=[];pc=entry;condition=False
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(400):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r4-r11, r15, r16':raise ValueError('UART configuration frame')
            saved={f'r{i}':r[f'r{i}'] for i in (*range(4,12),15,16)};r['r14']-=40
        elif op=='pop':
            if args!='r4-r11, r15, r16' or saved is None:raise ValueError('UART configuration restore')
            r.update(saved);r['r14']+=40
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('UART configuration ABI')
            return r['r0'],memory,trace
        elif op in ('ld.w','ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,source,off=m.groups();address=(r[source]+int(off,0))&0xffffffff
            if address&~3 not in memory:raise ValueError(('UART memory address',hex(address)))
            if op=='st.w':
                if address&3:raise ValueError('Unaligned UART store')
                memory[address]=r[reg];trace.append(('write',address,4,r[reg]))
            else:
                value=memory[address&~3]
                if op=='ld.b':value=(value>>((address&3)*8))&255
                r[reg]=value;trace.append(('read',address,1 if op=='ld.b' else 4,value))
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
        elif op=='bsr':
            target=int(args,0);kind=helpers[target]
            if kind=='fifo':
                if r['r0']!=base:raise ValueError('FIFO descriptor')
                trace.append(('fifo',base));result=depth
                if fifo_hook is not None:
                    result,reads=fifo_hook(memory[base+4],memory[memory[base+4]+0xf4])
                    trace.extend(('read',address,4,value) for address,value in reads)
                if changed_device is not None:memory[base+4]=changed_device
            elif kind=='irq':
                trace.append(('irq',r['r0'],r['r1'],r['r2']));result=0
                if irq_hook is not None:
                    for address,value in irq_hook(r['r0'],r['r1'],r['r2']):
                        memory[address]=value;trace.append(('write',address,4,value))
            else:
                trace.append((kind,*(r[f'r{i}'] for i in range(1 if kind=='uint' else 2 if kind=='fix' else 4))))
                result=arithmetic(kind,[r[f'r{i}'] for i in range(4)])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result&0xffffffff;r['r1']=(result>>32)&0xffffffff
        else:raise ValueError(('UART configuration opcode',hex(pc),op,args))
        pc=following
    raise ValueError('UART configuration execution bound')
