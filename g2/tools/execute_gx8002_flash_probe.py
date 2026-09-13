# SPDX-License-Identifier: MIT
"""Bounded decoded flash probe wrapper, scripted external reads/callbacks."""
import re
MASK=(1<<32)-1

def execute(code,entry,arguments,states,times,results,pointers=None,time_runner=None,probe_runner=None):
    r={f'r{i}':0xab000000+i for i in range(32)};r.update({f'r{i}':v for i,v in enumerate(arguments)});r['r14']=0x20070000;initial=dict(r);pc=entry;trace=[];indices=[0,0,0,0];condition=False
    def take(values,index):
        i=indices[index];assert i<len(values);indices[index]+=1;return values[i]
    for _ in range(500):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op=='push':
            assert args in ('r4-r11, r15','r4-r11, r15, r16');regs=[*range(4,12),15]+([16] if 'r16' in args else []);saved={f'r{i}':r[f'r{i}'] for i in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            r.update(saved);r['r14']+=4*len(regs);assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],trace
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='sub.64':
            d,a,b=[int(x[1:]) for x in p];v=((r[f'r{a}']|(r[f'r{a+1}']<<32))-(r[f'r{b}']|(r[f'r{b+1}']<<32)))&((1<<64)-1);r[f'r{d}']=v&MASK;r[f'r{d+1}']=v>>32
        elif op in ('ld.b','ld.w','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op=='ld.b':assert address==0x20026ff4;r[reg]=take(states,0);trace.append(('state',r[reg]))
            elif op=='ld.w':assert address==0x20026504;r[reg]=take(pointers,3) if pointers is not None else 0x10212340;trace.append(('callback_pointer',r[reg]))
            else:assert address==0x20026ff4;trace.append(('write_state',r[reg]&255))
        elif op in ('bsr','jsr'):
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0) if op=='bsr' else r[args]
            if target==0x1002585c:value=take(times,1);value=time_runner(value) if time_runner else value;trace.append(('time',value))
            else:assert target==(pointers[indices[2]] if pointers is not None else 0x10212340);trace.append(('probe',*(r[f'r{i}'] for i in range(4))));value=take(results,2);value=probe_runner(target,arguments,value) if probe_runner else value
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value&MASK;r['r1']=value>>32
        elif op in ('br','bt'):
            if op=='br' or condition:n=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):n=int(p[1],0)
        else:raise ValueError((op,args))
        pc=n
    raise AssertionError('Bound')
