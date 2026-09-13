# SPDX-License-Identifier: MIT
"""Check PDM setup call ordering, input normalization and fresh state reads."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_input_pdm import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,polarity,word,left,right,state,status,mutate,bindings):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=polarity,r14=0x20070000)
    initial=r.copy();pc=entry;saved=None;condition=False;trace=[];memory={0xa0a00000:word,0xa0a00028:left,0xa0a0002c:right,0x20027330:state}
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if saved is not None or args not in ('r4, r15','r4-r5, r15'):raise ValueError('PDM frame')
            frame=args;regs=['r4','r15'] if args=='r4, r15' else ['r4','r5','r15'];saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if saved is None or args!=frame:raise ValueError('PDM restore')
            for name,value in zip(regs,saved):r[name]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('PDM ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','lrw','movih'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op in ('or','ori'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0);r[p[0]]=a|b
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op=='bez':
            if not r[p[0]]:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('PDM memory operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&0xffffffff
            if address not in memory:raise ValueError('PDM memory address')
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xd408 else 0))&0xffffffff
            if target not in bindings:raise ValueError('PDM helper target')
            name=bindings[target];trace.append((name,r['r0'],r['r1']) if name=='gate' else (name,r['r0']))
            if mutate and name=='gate':
                for address in memory:memory[address]^=0x80000000
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=status
        else:raise ValueError('PDM instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('PDM bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('PDM stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd408','--stop-address=0xd454',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-input-pdm/pdm.disassembly.txt').read_text())
    bindings={0x10025080:'gate',0x1002598c:'delay'};cases=0
    for polarity,word,left,right,state,status,mutate in product((0,1,2,3,255,0x80000000,0xfffffffe,0xffffffff),(0,0x200,0x4000,0xffffffff),(0,0xfc00,0x12345678,0xffffffff),(0,0xfc00,0x87654321,0xffffffff),(0,2,0xffffffff),(0,7,0xffffffff),(False,True)):
        mask=0x80000000 if mutate else 0
        w,l,r,s=word^mask,left^mask,right^mask,state^mask
        control=(w&~0x200)|((polarity&1)<<9)
        trace=[('gate',8,1),('read',0xa0a00028,l),('write',0xa0a00028,l&~0xfc00),('read',0xa0a0002c,r),('write',0xa0a0002c,r&~0xfc00),('read',0xa0a00000,w),('write',0xa0a00000,control),('read',0xa0a00000,control),('write',0xa0a00000,control|0x4000),('read',0x20027330,s),('write',0x20027330,s|2),('delay',10)]
        wanted=(0,trace,{0xa0a00000:control|0x4000,0xa0a00028:l&~0xfc00,0xa0a0002c:r&~0xfc00,0x20027330:s|2})
        args=(polarity,word,left,right,state,status,mutate,bindings)
        if execute(old,0xd408,*args)!=wanted or execute(new,0x10203e7c,*args)!=wanted:raise ValueError('PDM ordered field oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Pinned compiler bitfield layout, ordered MMIO, low-bit polarity, state update and delay argument checked. Clock/delay helpers modeled with clobbers and optional gate mutation. Physical PDM input and delay timing unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-input-pdm-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('PDM cases:',r['decoded_cases'])
