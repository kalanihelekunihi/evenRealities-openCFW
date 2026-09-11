# SPDX-License-Identifier: MIT
import json,subprocess
from itertools import product
from build_gx8002_uart_write import build,ROOT
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode


def signed(x):return x if x<0x80000000 else x-0x100000000


def execute(code,entry,port,buffer,length,values,helper,transmit_hook=None):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=port,r1=buffer,r2=length,r14=0x20050000)
    initial=r.copy();pc=entry;trace=[];saved=None;condition=False;count=0
    for _ in range(10000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r7, r15':raise ValueError('Write frame')
            saved=[r[x] for x in ('r4','r5','r6','r7','r15')];r['r14']-=20
        elif op=='pop':
            if args!='r4-r7, r15' or saved is None:raise ValueError('Write restore')
            for reg,value in zip(('r4','r5','r6','r7','r15'),saved):r[reg]=value
            r['r14']+=20
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Write ABI')
            return r['r0'],trace
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('lsli','addu','subu'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a+b if op=='addu' else a-b)&0xffffffff
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='max.s32':r[p[0]]=max(signed(r[p[1]]),signed(r[p[2]]))&0xffffffff
        elif op=='bsr':
            if int(args,0)!=helper or count>=len(values):raise ValueError('Write helper target/count')
            trace.append(('transmit',r['r0'],r['r1']))
            if transmit_hook is not None:
                completed,nested=transmit_hook(r['r0'],r['r1'],count)
                trace.extend(nested)
                if not completed:return None,trace
            count+=1
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        elif op=='ldbi.b':
            reg=p[1].strip('()');index=(r[reg]-buffer)&0xffffffff
            if index>=len(values):raise ValueError('Write buffer access')
            value=values[index];trace.append(('read_byte',r[reg],value))
            r[p[0]]=value;r[reg]=(r[reg]+1)&0xffffffff
        else:raise ValueError('Write instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Write instruction bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Write stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xcb90','--stop-address=0xcbbc',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-write/write.disassembly.txt').read_text());cases=0
    for port,buffer,length,seed in product((0,1),(0x200a0000,0xfffffff0),(0,1,2,16,32,0xffffffff,0x80000000),(0,127,255)):
        count=max(0,signed(length));values=[(seed+i*37)&255 for i in range(count)]
        trace=[]
        for i,value in enumerate(values):trace.extend([('read_byte',(buffer+i)&0xffffffff,value),('transmit',0x20026a94+port*128,value)])
        expected=(count,trace)
        a=execute(old,0xcb90,port,buffer,length,values,0xc7d8)
        b=execute(new,0x10203604,port,buffer,length,values,0x1020324c)
        if a!=b or a!=expected:raise ValueError('Write contract mismatch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Transmit helper modeled; nested polling composition pending. Finite length corpus, no hardware or firmware integration qualification.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-write-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Write cases:',r['decoded_cases'])
