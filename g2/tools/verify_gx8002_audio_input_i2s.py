# SPDX-License-Identifier: MIT
"""Decode by-value I2S parameters and separate ordered register field writes."""
import json,re,random,subprocess
from itertools import product
from build_gx8002_audio_input_i2s import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
STACK=0x20070000


def execute(code,entry,parameters,word,state,status,mutate):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update({f'r{i}':parameters[i] for i in range(4)});r['r14']=STACK
    initial=r.copy();memory={STACK:parameters[4],STACK+4:parameters[5],0xa0a00004:word,0x20027330:state};trace=[];pc=entry;condition=False;pushed=False
    for _ in range(120):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if pushed or args!='r4, r15':raise ValueError('I2S saved frame')
            r['r14']-=8;memory[r['r14']]=r['r4'];memory[r['r14']+4]=r['r15'];pushed=True
        elif op=='rts':
            if not pushed or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('I2S ABI restore')
            if (memory[STACK],memory[STACK+4])!=parameters[4:]:raise ValueError('I2S caller stack overwritten')
            return r['r0'],trace,{address:memory[address] for address in (0xa0a00004,0x20027330)}
        elif op in ('mov','movi','lrw','movih'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='mvc':r[p[0]]=int(condition)
        elif op in ('or','ori'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);r[p[0]]=a|b
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op=='bf':
            if not condition:jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('I2S memory operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&0xffffffff
            stack=STACK-24<=address<=STACK+4 and address%4==0
            if address not in (0xa0a00004,0x20027330) and not stack:raise ValueError('I2S memory bounds')
            if op=='ld.w':
                if address not in memory:raise ValueError('I2S uninitialized stack read')
                r[reg]=memory[address]
                if not stack:trace.append(('read',address,r[reg]))
            else:
                memory[address]=r[reg]
                if not stack:trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xd454 else 0))&0xffffffff
            if target!=0x10025080:raise ValueError('I2S helper target')
            trace.append(('gate',r['r0'],r['r1']))
            if mutate:memory[0xa0a00004]^=0x80000000;memory[0x20027330]^=0x80000000
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=status
        else:raise ValueError('I2S instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('I2S bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('I2S stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd454','--stop-address=0xd4fc',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-input-i2s/i2s.disassembly.txt').read_text())
    corpus=[]
    for index,value in product(range(6),(0,1,2,3,7,15,0x80000000,0xffffffff)):
        p=[1,2,0,1,2,1];p[index]=value;corpus.append(tuple(p))
    rng=random.Random(804);corpus.extend(tuple(rng.getrandbits(32) for _ in range(6)) for _ in range(64))
    cases=0
    for parameters,word,state,status,mutate in product(corpus,(0,0xa5a5a5a5,0xffffffff),(0,4,0xffffffff),(0,7,0xffffffff),(False,True)):
        w=word^(0x80000000 if mutate else 0);s=state^(0x80000000 if mutate else 0);trace=[('gate',2,1)]
        fields=[(4,4,parameters[0]),(8,3,parameters[1]),(16,1,parameters[2]),(18,2,parameters[3]),(21,2,parameters[4]),(17,1,int(parameters[1]>=3)),(11,1,parameters[5]),(20,1,0),(2,1,0),(3,1,0),(30,1,1)]
        for low,bits,value in fields:
            trace.append(('read',0xa0a00004,w));mask=((1<<bits)-1)<<low;w=(w&~mask)|((value<<low)&mask);trace.append(('write',0xa0a00004,w))
        trace.extend([('read',0x20027330,s),('write',0x20027330,s|4)]);wanted=(0,trace,{0xa0a00004:w,0x20027330:s|4})
        args=(parameters,word,state,status,mutate)
        if execute(old,0xd454,*args)!=wanted or execute(new,0x10203ec8,*args)!=wanted:raise ValueError('I2S ordered parameter oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Pinned SDK six-word by-value ABI and compiler bitfield layout checked, including all stack arguments and raw unsigned format threshold. Gate effects modeled with caller clobbers and state mutation. Physical I2S/TDM input unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-input-i2s-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('I2S cases:',r['decoded_cases'])
