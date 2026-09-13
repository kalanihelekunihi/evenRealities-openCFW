# SPDX-License-Identifier: MIT
"""Decode configuration-callback field reads and by-value call arguments."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_config import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0x101f6a74;BOARD=0x20026d00;MASK=0xffffffff
COUNTS={0xc5b0:0,0xc590:0,0xd8dc:2,0xda6c:4,0xd988:4,0xd3a4:1,0xd860:1,0xd938:2,0xd408:1,0xd4fc:3,0xd8ac:1,0xd454:6,0xd8bc:1,0x105fc:2,0x10500:0,0xdafc:3}


def execute(code,entry,memory,frames,seed,mutation=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x20070000;initial=r.copy();memory=memory.copy();saved=None;events=[];pc=entry
    for _ in range(220):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+w
        if op=='push':
            if args!='r4-r5, r15' or saved is not None:raise ValueError('Frame')
            saved={v:r[v] for v in ('r4','r5','r15')};r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],events
        elif op in ('mov','movi'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)
        elif op in ('addi','subi','andi'):
            a,b=(r[p[0]],int(p[1],0)) if len(p)==2 else (r[p[1]],int(p[2],0))
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a&b)&MASK
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):nxt=int(p[1],0)
        elif op in ('ld.b','ld.h','ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0);n={'ld.b':1,'ld.h':2}.get(op,4)
            if address%n:raise ValueError('Alignment')
            if op=='st.w':
                if not r['r14']<=address<=r['r14']+4:raise ValueError('Stack write')
                for i,b in enumerate(r[reg].to_bytes(4,'little')):memory[address+i]=b
            else:
                if any(address+i not in memory for i in range(n)):raise ValueError('Read bounds')
                r[reg]=int.from_bytes(bytes(memory[address+i] for i in range(n)),'little')
        elif op=='bsr':
            target=(int(args,0)+(BASE if entry==0x107c0 else 0))&MASK;offset=target-BASE
            if offset not in COUNTS:raise ValueError('Call target')
            n=COUNTS[offset];values=[r[f'r{i}'] for i in range(min(n,4))]
            for i in range(max(0,n-4)):
                a=r['r14']+i*4;values.append(int.from_bytes(bytes(memory[a+j] for j in range(4)),'little'))
            events.append((offset,tuple(values)))
            if mutation:mutation(offset,memory)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed+0xab000000+i)&MASK
            r['r0']=BOARD if offset==0xc590 else frames if offset==0x10500 else seed
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')


def oracle(memory,frames,mutation=None):
    memory=memory.copy();events=[]
    def word(offset):return int.from_bytes(bytes(memory[BOARD+offset+i] for i in range(4)),'little')
    def words(offset,n):return tuple(word(offset+4*i) for i in range(n))
    def call(target,args=()):
        events.append((target,args))
        if mutation:mutation(target,memory)
    call(0xc5b0);call(0xc590);source=word(0)
    for i,mask in enumerate((1,2,4)):
        if not source&mask:continue
        offset=4+28*i
        call(0xd8dc,(mask,(word(offset)>>10)&1))
        call(0xda6c,(mask,)+words(offset+16,3))
        call(0xd988,(mask,)+words(offset+4,3))
        if i==0:
            call(0xd3a4,(word(92),));call(0xd860,(word(offset)&63,));call(0xd938,(mask,(word(offset)>>6)&15))
        else:
            call(0xd938,(mask,(word(offset)>>6)&15))
            if i==1:call(0xd408,(word(96),));call(0xd4fc,(2,0,1))
            else:
                call(0xd8ac,(3,));call(0xd454,words(100,6));call(0xd4fc,(4,1,0));call(0xd8bc,(0,))
    outputs=word(88)
    for mask in (1,2,4,8):
        if outputs&mask:call(0x105fc,(source,mask))
    call(0x10500);call(0xdafc,(1,0,frames))
    return 0,events


def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x107c0','--stop-address=0x10920',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-input-config/index.disassembly.txt').read_text());cases=0
    for source,outputs,seed in product((*range(16),0xffffffff),range(16),(0,1,0xffffffff,0xa5a5a5a5)):
        memory={BOARD+i:(i*37+seed)&255 for i in range(240)}
        for offset,value in ((0,source),(88,outputs)):
            for i,b in enumerate(value.to_bytes(4,'little')):memory[BOARD+offset+i]=b
        wanted=oracle(memory,seed)
        for code,entry in ((old,0x107c0),(new,0x10207234)):
            if execute(code,entry,memory,seed,seed)!=wanted:raise ValueError(('Configuration call effects',source,outputs,seed))
        cases+=1
    bitfield_cases=0
    for slot,bits in product(range(3),range(4096)):
        memory={BOARD+i:(i*37+11)&255 for i in range(240)}
        for offset,value in ((0,1<<slot),(88,15),(4+28*slot,0xfffff000|bits)):
            for i,b in enumerate(value.to_bytes(4,'little')):memory[BOARD+offset+i]=b
        wanted=oracle(memory,48)
        for code,entry in ((old,0x107c0),(new,0x10207234)):
            if execute(code,entry,memory,48,bits)!=wanted:raise ValueError('Bitfield sweep')
        bitfield_cases+=1
    mutation_cases=0
    for source,outputs,target in product(range(8),range(16),COUNTS):
        memory={BOARD+i:(i*37+11)&255 for i in range(240)}
        for offset,value in ((0,source),(88,outputs)):
            for i,b in enumerate(value.to_bytes(4,'little')):memory[BOARD+offset+i]=b
        def mutation(called,state):
            if called==target:
                for i in range(240):state[BOARD+i]^=(i*17+source+outputs+1)&255
        wanted=oracle(memory,48,mutation)
        for code,entry in ((old,0x107c0),(new,0x10207234)):
            if execute(code,entry,memory,48,source,mutation)!=wanted:raise ValueError(('Mutation',source,outputs,target))
        mutation_cases+=1
    return {'candidate':candidate,'bitfield_cases':bitfield_cases,'helper_mutation_cases':mutation_cases,'decoded_cases':cases,'source_admitted':False,'limits':['Independent call oracle, bitfield and by-value arguments, helper clobbers and saved ABI checked. Full12-bit config sweep and helper board mutations checked. Helpers modeled; source admission pending.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-audio-input-config-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
