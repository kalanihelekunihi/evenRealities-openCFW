# SPDX-License-Identifier: MIT
"""Decoded shutdown MMIO ordering and ABI across caller-clobbering gates."""
import json,re,subprocess
from build_gx8002_audio_output_init import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
BASE=0xa0b00000

def execute(code,entry,mode,seed,schedule):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=mode,r14=0x20070000);saved=r.copy();stack={};trace=[];memory={BASE+i:seed for i in (0,4,12,32)};pc=entry;condition=False;armed=False;polls=0
    for _ in range(200):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4, r15':raise ValueError('Init frame')
            r['r14']-=8;stack[r['r14']]=r['r4'];stack[r['r14']+4]=r['r15']
        elif op=='pop':
            if args!='r4, r15':raise ValueError('Init restore')
            r['r4']=stack[r['r14']];r['r15']=stack[r['r14']+4];r['r14']+=8
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Init ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='bez':
            if not r[p[0]]:jump=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op in ('andi','andni'):r[p[0]]=r[p[1]]&(int(p[2],0) if op=='andi' else ~int(p[2],0))
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='bclri':r[p[0]] &= ~(1<<int(p[1],0))
        elif op=='nor':r[p[0]]=~(r[p[1]]|r[p[2]])&MASK
        elif op=='and':r[p[0]] &= r[p[1]]
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='bnez':
            if r[p[0]]:jump=int(p[1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Init operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a not in memory:raise ValueError('Init MMIO address')
            if op=='ld.w':
                if a==BASE+12 and armed:
                    polls+=1
                    memory[a]&=~(1<<20)
                    if schedule is not None and polls>schedule:memory[a]|=1<<20
                r[reg]=memory[a];trace.append(('read',a,r[reg]))
                if a==BASE+12 and armed and schedule is None and polls==16:return 'waiting_prefix',trace,memory
            else:
                memory[a]=r[reg];trace.append(('write',a,r[reg]))
                if a==BASE+12 and not armed:armed=True
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe4a4 else 0))&MASK
            if target!=0x10025080:raise ValueError('Init gate target')
            trace.append(('gate',r['r0'],r['r1']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Init instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Init bound')

def oracle(mode,seed,schedule):
    memory={BASE+i:seed for i in (0,4,12,32)};trace=[('gate',11,1),('gate',15,1)]
    def update(offset,value):trace.extend((('read',BASE+offset,memory[BASE+offset]),('write',BASE+offset,value)));memory[BASE+offset]=value
    for bit in (2,4,8):update(32,memory[BASE+32]|bit)
    update(4,(seed&~0xc00)|(0x400 if mode==2 else ((mode<<10)&0xc00)))
    if mode==2:update(4,memory[BASE+4]&~128)
    update(12,seed|(1<<22))
    for _ in range(16 if schedule is None else schedule):
        memory[BASE+12]&=~(1<<20);trace.append(('read',BASE+12,memory[BASE+12]))
    if schedule is None:return 'waiting_prefix',trace,memory
    memory[BASE+12]|=1<<20;trace.append(('read',BASE+12,memory[BASE+12]));update(12,1<<20);update(0,seed|(1<<31))
    return 0,trace,memory

def verify():
    from itertools import product
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Init stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe4a4','--stop-address=0xe51c',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-init/bits.disassembly.txt').read_text());cases=0
    for mode,seed,schedule in product(tuple(range(256))+(0x7fffffff,0x80000000,0xffffffff),(0,0xffffffff,0xa5a5a5a5),(0,1,2,7,16,None)):
        wanted=oracle(mode,seed,schedule)
        for code,entry in ((old,0xe4a4),(new,0x10204f18)):
            if execute(code,entry,mode,seed,schedule)!=wanted:raise ValueError(('Init effects',entry,mode,seed,schedule))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Clock gates modeled with caller clobbers. Reset completion injected after selected poll counts; no completion verified through16 polls without return. Real peripheral timing and hardware acknowledgment semantics remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-init-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
