# SPDX-License-Identifier: MIT
"""Suspend with decoded interrupt helpers and independent ordered effects."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_suspend import build,ROOT,IMAGE_SHA,sha,Elf32
from build_gx8002_audio_output_bits import build as bit_build
from verify_gx8002_audio_output_bits import execute as bit_execute
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
BASE=0xa0b00000
def execute(code,entry,flag26,flag27,seed,helper_code,stock):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x20070000;r['r0']=0x20010000;saved=r.copy();stack={};trace=[];memory={BASE:seed,BASE+8:seed,BASE+12:seed,0x2001001a:flag26,0x2001001b:flag27};pc=entry
    for _ in range(64):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r15':raise ValueError('Exit frame')
            r['r14']-=4;stack[r['r14']]=r['r15']
        elif op=='pop':
            if args!='r15':raise ValueError('Exit restore')
            r['r15']=stack[r['r14']];r['r14']+=4
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Exit ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
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
            if a not in memory or (a>=BASE)!=(op.endswith('w')):raise ValueError('Resume access width/address')
            if op.startswith('ld'):r[reg]=memory[a];trace.append(('read',a,r[reg]))
            else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe44c else 0))&MASK
            if target==0x10025080:trace.append(('gate',r['r0'],r['r1']))
            elif target in (0x102049d8,0x102049c8):
                if (r['r0'],r['r1'])!=(BASE,0):raise ValueError('Suspend helper args')
                offset=0 if target==0x102049d8 else 8
                trace.append(('helper',target,BASE,0))
                result,nested,word=bit_execute(helper_code,target-0x101f6a74 if stock else target,BASE,0,memory[BASE+offset],offset)
                trace.extend(nested);memory[BASE+offset]=word
            else:raise ValueError('Suspend helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Exit instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Exit bound')

def verify():
    candidate=build();helpers=bit_build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Suspend stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xdf54','--stop-address=0xe4a4',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-suspend/bits.disassembly.txt').read_text());helper_new=decode((ROOT/'build/gx8002-audio-output-bits/bits.disassembly.txt').read_text());cases=0
    for flag26,flag27,seed in product((0,1,2,127,128,255),(0,1,2,127,128,255),(0,0xffffffff,0xa5a5a5a5)):
        memory={BASE:seed,BASE+8:seed,BASE+12:seed,0x2001001a:flag26,0x2001001b:flag27};trace=[]
        def update(offset,mask):
            a=BASE+offset;trace.append(('read',a,memory[a]));memory[a]&=mask;trace.append(('write',a,memory[a]))
        trace.append(('read',0x2001001b,flag27))
        if flag27:update(8,MASK^1);update(12,1)
        trace.append(('read',0x2001001a,flag26))
        if flag26:
            trace.append(('helper',0x102049d8,BASE,0));update(0,MASK^2)
            trace.append(('helper',0x102049c8,BASE,0));update(8,MASK^2);update(12,2)
        trace.extend((('gate',11,0),('gate',15,0)));wanted=(0,trace,memory)
        if execute(old,0xe44c,flag26,flag27,seed,old,True)!=wanted or execute(new,0x10204ec0,flag26,flag27,seed,helper_new,False)!=wanted:raise ValueError('Suspend effects mismatch')
        cases+=1
    return {'candidate':candidate,'helpers':helpers,'nested_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Actual decoded interrupt helper effects propagate through suspend. Gate internals and physical status register semantics modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-suspend-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['nested_cases'])
