# SPDX-License-Identifier: MIT
"""Resume ordering under gate-induced state mutations and caller clobbers."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_resume import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0xa0b00008
def execute(code,entry,flag26,flag27,seed,mutate):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x20070000;r['r0']=0x20010000;saved=r.copy();stack={};trace=[];memory={ADDRESS:seed,0x2001001a:flag26,0x2001001b:flag27};pc=entry
    for _ in range(64):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4, r15':raise ValueError('Exit frame')
            r['r14']-=8;stack[r['r14']]=r['r4'];stack[r['r14']+4]=r['r15']
        elif op=='pop':
            if args!='r4, r15':raise ValueError('Exit restore')
            r['r4']=stack[r['r14']];r['r15']=stack[r['r14']+4];r['r14']+=8
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Exit ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='addi':r[p[0]]=(r[p[1]] if len(p)==3 else r[p[0]])+int(p[-1],0)
        elif op=='bez':
            if not r[p[0]]:jump=int(p[1],0)
        elif op=='bclri':r[p[0]] &= ~(1<<int(p[1],0))
        elif op=='nor':r[p[0]]=~(r[p[1]]|r[p[2]])&MASK
        elif op=='and':r[p[0]] &= r[p[1]]
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='bnez':
            if r[p[0]]:jump=int(p[1],0)
        elif op in ('ld.w','st.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Exit operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a not in memory or (a==ADDRESS)!=(op.endswith('w')):raise ValueError('Resume access width/address')
            if op.startswith('ld'):r[reg]=memory[a];trace.append(('read',a,r[reg]))
            else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe7a8 else 0))&MASK
            if target!=0x10025080:raise ValueError('Exit gate target')
            trace.append(('gate',r['r0'],r['r1']))
            if mutate and r['r0']==15:
                memory[0x2001001a]^=255;memory[0x2001001b]^=255;memory[ADDRESS]^=0xffffffff
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Exit instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Exit bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Resume stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe7a8','--stop-address=0xe7e0',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-resume/bits.disassembly.txt').read_text());cases=0
    for flag26,flag27,seed,mutate in product((0,1,2,127,128,255),(0,1,2,127,128,255),(0,0xffffffff,0xa5a5a5a5),(False,True)):
        memory={ADDRESS:seed,0x2001001a:flag26,0x2001001b:flag27};trace=[('gate',11,1),('gate',15,1)]
        if mutate:memory[0x2001001a]^=255;memory[0x2001001b]^=255;memory[ADDRESS]^=0xffffffff
        trace.append(('read',0x2001001b,memory[0x2001001b]))
        if memory[0x2001001b]:
            trace.append(('read',ADDRESS,memory[ADDRESS]));memory[ADDRESS]|=1;trace.append(('write',ADDRESS,memory[ADDRESS]))
        trace.append(('read',0x2001001a,memory[0x2001001a]))
        if memory[0x2001001a]:memory[0x2001001a]=0;trace.append(('write',0x2001001a,0))
        wanted=(0,trace,memory);args=(flag26,flag27,seed,mutate)
        if execute(old,0xe7a8,*args)!=wanted or execute(new,0x1020521c,*args)!=wanted:raise ValueError('Resume ordered effects')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Flags and IRQ can mutate during second gate call; reads must observe new state. Gate internals/physical effects remain modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-resume-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
