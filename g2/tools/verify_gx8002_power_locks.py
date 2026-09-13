# SPDX-License-Identifier: MIT
"""Decode lock allocation and query, including aliased publication."""
import json,re,subprocess,random
from build_gx8002_power_locks import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word,BASE,MASK

def execute(code,entry,memory,destination):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r0']=destination;initial=r.copy();pc=entry;events=[];condition=False
    for _ in range(250):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],memory,events
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('addi','subi'):r[p[0]]=(r[p[0]]+(1 if op=='addi' else -1)*int(p[1],0))&MASK
        elif op=='lsl':
            if r[p[2]]>31:raise ValueError('Unexpected shift')
            r[p[0]]=(r[p[1]]<<r[p[2]])&MASK
        elif op=='and':r[p[0]]=r[p[1]]&r[p[2]]
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='br':nxt=int(args,0)
        elif op in ('bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=word(memory,address);events.append(('read',address,r[reg]))
            else:word(memory,address,r[reg]);events.append(('write',address,r[reg]))
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')

def oracle(memory,destination):
    memory=memory.copy();allocated=word(memory,BASE+4);events=[('read',BASE+4,allocated)]
    free=(~allocated)&MASK
    if not free:return MASK,memory,events
    bit=free&-free;handle=bit.bit_length();word(memory,destination,handle);events.append(('write',destination,handle))
    current=word(memory,BASE+4);events.append(('read',BASE+4,current));word(memory,BASE+4,current|bit);events.append(('write',BASE+4,current|bit))
    result=word(memory,destination);events.append(('read',destination,result))
    return result,memory,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10cfc','--stop-address=0x10d94',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-power-locks/buffers.disassembly.txt').read_text());rng=random.Random(20260912)
    masks=sorted({0,MASK,*((1<<i)-1 for i in range(33)),*(MASK^(1<<i) for i in range(32)),*(rng.getrandbits(32) for _ in range(1000))});cases=0
    for allocated in masks:
        for destination in range(BASE-16,BASE+24,4):
            memory={BASE+i:(i*37+allocated)&255 for i in range(-20,32)};word(memory,BASE+4,allocated);word(memory,BASE,allocated)
            expected=oracle(memory,destination)
            for code,base in ((old,0),(new,0x101f6a74)):
                if execute(code,0x10cfc+base,memory,destination)!=expected:raise ValueError(('Allocate',allocated,destination))
                if execute(code,0x10d84+base,memory,destination)!=(int(allocated!=0),memory,[('read',BASE,allocated)]):raise ValueError('Query')
            cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Ordered full-memory and ABI comparison includes all first-free bits, exhausted bitmap, random masks, and aligned output aliases. Unaligned pointers and asynchronous changes are not qualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-power-locks-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
