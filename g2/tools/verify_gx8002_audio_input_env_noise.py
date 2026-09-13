# SPDX-License-Identifier: MIT
"""Decode noise hysteresis, wrapping counters and exact field access order."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_env_noise import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0x101f6a74;COUNTERS=0x2002dfac;CONTEXT=0x20050000;MASK=0xffffffff


def execute(code,entry,noise,memory,context=CONTEXT):
    r={f'r{i}':0xabc00000+i for i in range(32)};r.update(r0=context,r14=0x20070000);initial=r.copy();saved=None;pc=entry;condition=False;events=[]
    for _ in range(55):
        op,args,w=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+w
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],events
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmplti':condition=(r[p[0]] if r[p[0]]<0x80000000 else r[p[0]]-0x100000000)<int(p[1],0)
        elif op in ('bt','br'):
            if op=='br' or condition:nxt=int(args,0)
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low
            r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op in ('ld.w','ld.b','st.w','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0);n=4 if op.endswith('.w') else 1
            if address%n or any(address+i not in memory for i in range(n)):raise ValueError('Memory bounds')
            if op.startswith('ld'):
                value=int.from_bytes(bytes(memory[address+i] for i in range(n)),'little');r[reg]=value;events.append(('read',address,n,value))
            else:
                value=r[reg]&((1<<(8*n))-1);events.append(('write',address,n,value))
                for i,b in enumerate(value.to_bytes(n,'little')):memory[address+i]=b
        elif op=='bsr':
            if (int(args,0)+(BASE if entry==0x10b54 else 0))&MASK!=0x102047ac:raise ValueError('Helper')
            events.append(('noise',))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=noise
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')


def oracle(noise,memory,context=CONTEXT):
    events=[('noise',)]
    def read(a,n):
        v=int.from_bytes(bytes(memory[a+i] for i in range(n)),'little');events.append(('read',a,n,v));return v
    def write(a,n,v):
        events.append(('write',a,n,v))
        for i,b in enumerate(v.to_bytes(n,'little')):memory[a+i]=b
    slot=0 if noise>66060288 else 1 if noise>6291456 else 2
    count=(read(COUNTERS+4*slot,4)+1)&MASK;write(COUNTERS+4*slot,4,count)
    signed=count if count<0x80000000 else count-0x100000000
    changed=signed>(50 if slot==1 else 150)
    if changed:
        for reset in ((1,2) if slot==0 else (0,2)):write(COUNTERS+4*reset,4,0)
        byte=read(context+14,1);value=2-slot
        write(context+14,1,(byte&248)|value);write(COUNTERS+12,4,value)
    else:
        value=read(COUNTERS+12,4);byte=read(context+14,1);write(context+14,1,(byte&248)|(value&7))
    return 0,events


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10b54','--stop-address=0x10bd0',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-input-env-noise/index.disassembly.txt').read_text());cases=0
    for noise,count,last,byte in product((0,6291456,6291457,66060288,66060289,0xffffffff),(0,49,50,149,150,151,0x7ffffffe,0x7fffffff,0x80000000,0xffffffff),(0,1,2,7,0xffffffff),range(256)):
        memory={COUNTERS+i:0xa5 for i in range(-4,20)};memory.update({CONTEXT+i:0x5a for i in range(32)})
        for slot,value in enumerate((count,count,count,last)):
            for i,b in enumerate(value.to_bytes(4,'little')):memory[COUNTERS+slot*4+i]=b
        memory[CONTEXT+14]=byte;expected=memory.copy();wanted=oracle(noise,expected)
        for code,entry in ((old,0x10b54),(new,0x102075c8)):
            actual=memory.copy()
            if execute(code,entry,noise,actual)!=wanted or actual!=expected:raise ValueError('Noise state effects')
        cases+=1
    alias_cases=0
    for context,noise,count in product(range(COUNTERS-44,COUNTERS+20,4),(0,6291457,66060289),(0,50,150,151,0x7fffffff,0xffffffff)):
        memory={a:0xa5 for a in range(COUNTERS-48,COUNTERS+56)}
        for slot,value in enumerate((count,count,count,0xffffffff)):
            for i,b in enumerate(value.to_bytes(4,'little')):memory[COUNTERS+4*slot+i]=b
        expected=memory.copy();wanted=oracle(noise,expected,context)
        for code,entry in ((old,0x10b54),(new,0x102075c8)):
            actual=memory.copy()
            if execute(code,entry,noise,actual,context)!=wanted or actual!=expected:raise ValueError('Aliased noise state')
        alias_cases+=1
    return {'candidate':candidate,'alias_cases':alias_cases,'decoded_cases':cases,'source_admitted':False,'limits':['Exact ordered byte/word effects, counter wraparound and neighboring bit preservation checked. Distinct and overlapping context/state storage checked; helper modeled. Admission pending.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-env-noise-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
