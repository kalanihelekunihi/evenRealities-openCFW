# SPDX-License-Identifier: MIT
"""Decoded shutdown MMIO ordering and ABI across caller-clobbering gates."""
import json,re,subprocess
from build_gx8002_audio_output_exit import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0xa0b00020

def execute(code,entry,seed):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x20070000;saved=r.copy();stack={};trace=[];word=seed;pc=entry
    for _ in range(64):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4, r15':raise ValueError('Exit frame')
            r['r14']-=8;stack[r['r14']]=r['r4'];stack[r['r14']+4]=r['r15']
        elif op=='pop':
            if args!='r4, r15':raise ValueError('Exit restore')
            r['r4']=stack[r['r14']];r['r15']=stack[r['r14']+4];r['r14']+=8
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Exit ABI')
            return r['r0'],trace,word
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bclri':r[p[0]] &= ~(1<<int(p[1],0))
        elif op=='nor':r[p[0]]=~(r[p[1]]|r[p[2]])&MASK
        elif op=='and':r[p[0]] &= r[p[1]]
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='bnez':
            if r[p[0]]:jump=int(p[1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Exit operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a!=ADDRESS:raise ValueError('Exit MMIO address')
            if op=='ld.w':r[reg]=word;trace.append(('read',a,word))
            else:word=r[reg];trace.append(('write',a,word))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe8d0 else 0))&MASK
            if target!=0x10025080:raise ValueError('Exit gate target')
            trace.append(('gate',r['r0'],r['r1']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Exit instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Exit bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Exit stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe8d0','--stop-address=0xe900',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-exit/bits.disassembly.txt').read_text());cases=0
    for seed in (*range(256),0xffffffff,0x80000000,0xa5a5a5a5):
        word=seed;trace=[]
        for bit in (1,2,3):trace.append(('read',ADDRESS,word));word &= ~(1<<bit);trace.append(('write',ADDRESS,word))
        trace.extend((('gate',11,0),('gate',15,0)));wanted=(0,trace,word)
        if execute(old,0xe8d0,seed)!=wanted or execute(new,0x10205344,seed)!=wanted:raise ValueError('Exit ordered effects')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Separate word updates and ordered gate arguments preserved with caller clobbers. Gate internals and physical clock behavior modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-exit-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
