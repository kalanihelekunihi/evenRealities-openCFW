# SPDX-License-Identifier: MIT
"""Decoded power initialization, callback mutation, memory ordering and ABI."""
import json,re,subprocess
from itertools import product
from build_gx8002_power_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0x2002dfbc
MASK=0xffffffff

def word(memory,address,value=None):
    if value is None:return sum(memory[address+i]<<(8*i) for i in range(4))
    for i in range(4):memory[address+i]=(value>>(8*i))&255

def mutate(memory,policy,call):
    if policy==1:word(memory,BASE+12,0)
    if policy==2:word(memory,BASE+12,8)
    if policy==3:word(memory,BASE+12,call+1)
    if policy==4:
        for i in range(call+1,8):
            word(memory,BASE+80+i*8,0x10210000+i*4)
            word(memory,BASE+84+i*8,0xff000000+i)

def execute(code,entry,mode,memory,policy,result):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();saved=None;events=[];pc=entry;condition=False;calls=0
    for _ in range(180):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r6, r15' or saved is not None:raise ValueError('Frame')
            saved={key:r[key] for key in ('r4','r5','r6','r15')};r['r14']-=16
        elif op=='pop':
            if args!='r4-r6, r15' or saved is None:raise ValueError('Restore')
            r.update(saved);r['r14']+=16
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],memory,events
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op=='ld.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(off,0))&MASK
            r[reg]=word(memory,address);events.append(('read',address,r[reg]))
        elif op in ('bsr','jsr'):
            target=((int(args,0)+(0x101f6a74 if entry<0x100000 else 0))&MASK) if op=='bsr' else r[args]
            if op=='jsr':
                events.append(('callback',target,r['r0']));mutate(memory,policy,calls);calls+=1;value=result
            elif target==0x10024940:events.append(('wakeup',));value=mode
            elif target==0x102099cc:
                if (r['r0'],r['r1'],r['r2'])!=(BASE,0,144):raise ValueError('Clear extent')
                events.append(('clear',BASE,144))
                for i in range(144):memory[BASE+i]=0
                value=BASE
            else:raise ValueError('Helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xcd000000+i
            r['r0']=value
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')

def oracle(mode,memory,policy):
    memory=memory.copy();events=[('wakeup',)]
    if mode<2:
        events.append(('clear',BASE,144))
        for i in range(144):memory[BASE+i]=0
        return 1,memory,events
    i=0
    while True:
        count=word(memory,BASE+12);events.append(('read',BASE+12,count))
        if i>=count:break
        address=BASE+80+i*8;callback=word(memory,address);private=word(memory,address+4)
        events.extend([('read',address,callback),('read',address+4,private),('callback',callback,private)])
        mutate(memory,policy,i);i+=1
    return 0,memory,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10c0c','--stop-address=0x10c4c',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-power-initialize/buffers.disassembly.txt').read_text());cases=0
    for mode,count,policy,result,seed in product((0,1,2,3,0x7fffffff,0x80000000,0xffffffff),range(9),range(5),(0,1,0x80000000,0xffffffff),range(3)):
        memory={BASE+i:(i*37+seed*67)&255 for i in range(-16,160)};word(memory,BASE+12,count)
        for i in range(8):word(memory,BASE+80+i*8,0x10200000+i*4);word(memory,BASE+84+i*8,(seed*0x80000000+i)&MASK)
        expected=oracle(mode,memory,policy)
        for code,base in ((old,0),(new,0x101f6a74)):
            if execute(code,0x10c0c+base,mode,memory,policy,result)!=expected:raise ValueError(('Initialization',mode,count,policy,result,seed))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Exact ordered reads, callbacks, clear extent, guard bytes and saved ABI checked; callbacks may shrink/grow counts or replace future entries. Helpers modeled; valid registry counts 0..8 only; physical wakeup and asynchronous mutation not qualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-power-initialize-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
