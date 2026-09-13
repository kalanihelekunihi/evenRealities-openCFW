# SPDX-License-Identifier: MIT
"""Decoded stock/source logfbank setup with independent ordered-MMIO oracle."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_logfbank import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,config,seed):
    r={f'r{i}':0x98760000+i for i in range(32)}
    r.update(zip(('r0','r1','r2','r3'),config[:4]));r['r14']=0x20070000
    initial=r.copy();stack={r['r14']:config[4]}
    memory={a:seed^a for a in (0xa0a00108,0xa0a0015c,0xa0a00160,0xa0a00164,0xa0a00104,0x20027334)}
    trace=[];pc=entry
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Logfbank ABI')
            if stack[initial['r14']]!=config[4]:raise ValueError('Caller stack mutated')
            return r['r0'],trace,memory
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('subi','addi','andi','andni','ori','bseti','lsli'):
            value=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0)
            r[p[0]]={'subi':lambda:value-n,'addi':lambda:value+n,'andi':lambda:value&n,'andni':lambda:value&~n,'ori':lambda:value|n,'bseti':lambda:value|(1<<n),'lsli':lambda:value<<n}[op]()&0xffffffff
        elif op in ('mult','subu','or','and','divu'):
            left=r[p[1]] if len(p)==3 else r[p[0]];right=r[p[-1]]
            if op=='divu' and right==0:raise ValueError('Unqualified zero divisor')
            r[p[0]]={'mult':lambda:left*right,'subu':lambda:left-right,'or':lambda:left|right,'and':lambda:left&right,'divu':lambda:left//right}[op]()&0xffffffff
        elif op=='bnez':
            if r[p[0]]:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op=='ins':
            high,low=int(p[2]),int(p[3]);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Logfbank operand')
            reg,base,offset=m.groups();address=(r[base]+int(offset,0))&0xffffffff
            if initial['r14']-16<=address<=initial['r14'] and address%4==0:
                if op=='ld.w':r[reg]=stack[address]
                else:stack[address]=r[reg]
            elif address in memory:
                if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
                else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
            else:raise ValueError('Logfbank unexpected address '+hex(address))
        else:raise ValueError('Logfbank instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Logfbank bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Logfbank stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd60c','--stop-address=0xd6b8',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-output-logfbank/logfbank.disassembly.txt').read_text());cases=0
    for buffer,size,frames,endian,source,seed in product((0,0x20040000,0x20040001,0x20040007,0xfffffff8),(0,1,79,80,160,240,320,0xffffffb0,0xffffffff),(1,2,3,80,81,0xffffffff),(0,1,3,4,0xffffffff),(0,1,4,7,8,0xffffffff),(0,0xa5a5a5a5,0xffffffff)):
        memory={a:seed^a for a in (0xa0a00108,0xa0a0015c,0xa0a00160,0xa0a00164,0xa0a00104,0x20027334)};trace=[]
        def write(a,value):memory[a]=value;trace.append(('write',a,value))
        def field(high,low,value):
            a=0xa0a00108;trace.append(('read',a,memory[a]));mask=((1<<(high-low+1))-1)<<low;write(a,(memory[a]&~mask)|((value<<low)&mask))
        result=0xffffffff
        if buffer%8==0 and size%80==0 and size%frames==0:
            result=0;field(20,19,endian);field(18,16,source)
            for a,value in ((0xa0a0015c,frames),(0xa0a00160,buffer),(0xa0a00164,size),(0xa0a00104,8192)):write(a,value)
            field(22,22,1);field(23,23,0);field(21,21,1)
            a=0x20027334;trace.append(('read',a,memory[a]));write(a,memory[a]|4)
        wanted=result,trace,memory;config=(buffer,size,frames,endian,source)
        if execute(old,0xd60c,config,seed)!=wanted or execute(new,0x10204080,config,seed)!=wanted:raise ValueError('Logfbank oracle '+repr(config))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Nonzero frame count required: hardware division by zero is unqualified. Alignment, both divisibility gates, field narrowing, ordered volatile writes and aggregate ABI checked. Physical logfbank production unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-logfbank-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Logfbank cases:',r['decoded_cases'])
