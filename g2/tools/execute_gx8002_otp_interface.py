#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute full flash initialization with continuous register and stack state."""
import contextlib
import io
import json
import re
import subprocess
from compare_gx8002_flash_interface_selection import verify as verify_selection, ROOT, decode


def execute(code,pc,delta,seed,configuration_value,discovery,first,second,arguments):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)}
    assert len(arguments)==4
    r.update({f'r{i}':value for i,value in enumerate(arguments)})
    r['r14']=0x2002f7fc;top=r['r14'];stack={};trace=[];saved=False;initial=r.copy();frame_top=top;loads=0;carry=None;low=top
    for _ in range(250):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args not in ('r4-r7, r15',) or saved:raise ValueError('unexpected setup frame')
            names=['r4','r5','r6','r7','r15']
            r['r14']-=4*len(names);frame_top=r['r14']
            stack.update({r['r14']+i*4:r[n] for i,n in enumerate(names)});saved=True
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi','lsli','rotli'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b if op=='lsli' else (a<<b)|(a>>(32-b)))&0xffffffff
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op in ('st.w','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown setup store')
            value,base,off=m.groups();address=r[base]+int(off,0)
            if r['r14']<=address<top:
                if address>=frame_top:raise ValueError('overwrites saved register')
                stack[address]=r[value] if op=='st.w' else r[value]&255
            elif address in (0xa0300090,0xa2000008,0xa200002c,0xa20000f0,0xa2000014,0xa200001c,0x200264fc,0x20026500):
                trace.append(['write',address,r[value]])
            else:raise ValueError('unexpected setup address')
        elif op=='bsr':
            target=int(args,0)+delta
            if target==0x10025d74:
                pointer=r['r1']
                if r['r0']!=9 or pointer!=r['r14']+24 or stack.get(pointer)!=0:raise ValueError('configuration input mismatch')
                trace.append(['call',target,9,'initialized-input',0])
                if configuration_value!=0:raise ValueError('initializer configuration must remain zero')
                trace.extend([['write',0xa000003c,stack[pointer]&1],['write',0x20027314,stack[pointer]&1]])
            elif target==0x1002553c:
                trace.append(['irq',r['r0'],r['r1'],r['r2']])
            elif target==0x10023734:trace.append(['status',second])
            elif target==0x100236dc:
                if r['r1']!=r['r14']+23 or r['r1'] not in stack:raise ValueError('command pointer')
                trace.append(['command',r['r0'],stack[r['r1']],r['r2']])
            elif target==0x10025080:
                trace.append(['call',target,r['r0'],r['r1']])
            elif target in (0x1002364c,0x1002375c,0x10024190,0x100242b4,0x10024330,0x100242ec,0x100246c4,0x1002374c):trace.append(['call',target])
            elif target==0x1002436c:
                try:arguments=[r[f'r{i}'] for i in range(4)]+[stack[r['r14']+i*4] for i in range(5)]
                except KeyError:raise ValueError('uninitialized XIP argument')
                trace.append(['xip',arguments])
            else:raise ValueError('unknown setup call')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xdeadbeef^(i*0x11111111))&0xffffffff
            if target==0x10024190:r['r0']=discovery&0xffffffff
            if target==0x10023734:r['r0']=second
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('andi','andni','ori'):
            a=r[p[1]];b=int(p[2],0);r[p[0]]=(a&b if op=='andi' else a&~b if op=='andni' else a|b)&0xffffffff
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown state load')
            dst,reg,offset=m.groups();address=r[reg]+int(offset,0)
            if address==0x200264f0:
                loads+=1
                if loads>1:raise ValueError('excess state reads')
                value=0x20028000 if loads==1 else 0x20029000
            elif address==0x20028004 and loads==1:value=first
            elif address==0x20029004 and loads==2:value=second
            else:raise ValueError('unknown state address')
            r[dst]=value;trace.append(['read',address,value])
        elif op in ('cmpne','cmplt','cmphs','cmphsi'):
            a=r[p[0]];b=int(p[1],0) if op=='cmphsi' else r[p[1]]
            if op=='cmplt':a=a-(1<<32) if a&0x80000000 else a;b=b-(1<<32) if b&0x80000000 else b
            carry=a!=b if op=='cmpne' else a<b if op=='cmplt' else a>=b
        elif op in ('br','bt','bf','bnez'):
            if op in ('bt','bf') and carry is None:raise ValueError('undefined branch')
            if op=='br' or op=='bnez' and r[p[0]]!=0 or op in ('bt','bf') and carry==(op=='bt'):following=int(p[-1],0)
        elif op=='pop':
            expected='r4-r7, r15'
            if args!=expected or r['r14']!=frame_top:raise ValueError('unbalanced return frame')
            for i,name in enumerate(names):r[name]=stack[frame_top+i*4]
            r['r14']+=len(names)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI mismatch')
            return {'result':r['r0'],'trace':trace,'frame_bytes':top-low}
        else:raise ValueError('unsupported full instruction '+op)
        low=min(low,r['r14']);pc=following
    raise ValueError('setup execution bound exceeded')
