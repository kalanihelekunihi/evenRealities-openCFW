# SPDX-License-Identifier: MIT
"""Execute original jump-table DAC sequence and complete source helper calls."""
import json,re,struct,subprocess
from itertools import product
from build_gx8002_audio_output_lodac import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
BASE=0xa0b00000
MASK=0xffffffff

def execute(code,entry,selector,level,seed,targets):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x20070000;saved=r.copy();stack={};depth=0
    memory={BASE+4:selector,BASE+36:level,BASE+40:seed};trace=[];pc=entry;condition=False
    for _ in range(400):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r6, r15':raise ValueError('Lodac frame')
            r['r14']-=16
            for i,name in enumerate(('r4','r5','r6','r15')):stack[r['r14']+4*i]=r[name]
        elif op in ('rts','pop'):
            if op=='rts' and depth:jump=r['r15'];depth-=1
            else:
                if op=='pop':
                    if args!='r4-r6, r15':raise ValueError('Lodac restore')
                    for i,name in enumerate(('r4','r5','r6','r15')):r[name]=stack[r['r14']+4*i]
                    r['r14']+=16
                if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Lodac ABI')
                return trace,memory
        elif op=='bsr':r['r15']=pc+width;jump=int(args,0);depth+=1
        elif op in ('mov','movi','movih','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op=='and':r[p[0]] &= r[p[1]]
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='bclri':r[p[0]] &= ~(1<<int(p[1],0))
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='jmp':jump=r[args]-0x101f6a74
        elif op=='ldr.w':
            if args!='r3, (r3, r1 << 2)' or r['r3']!=0x1020a8f4 or r['r1']>=7:raise ValueError('Lodac table access')
            r['r3']=targets[r['r1']]
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Lodac operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a not in memory:raise ValueError('Lodac MMIO bounds')
            if op=='ld.w':r[reg]=memory[a];trace.append(('read',a,r[reg]))
            else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
        else:raise ValueError('Lodac instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Lodac instruction bound')

def oracle(selector,level,seed):
    memory={BASE+4:selector,BASE+36:level,BASE+40:seed};trace=[]
    def read(a):trace.append(('read',a,memory[a]));return memory[a]
    def write(v):memory[BASE+40]=v;trace.append(('write',BASE+40,v))
    def pulse():write(read(BASE+40)|2);write(read(BASE+40)&~2)
    write(read(BASE+40)|1);pulse();pulse()
    choice=(read(BASE+4)>>4)&7
    write((0xa85,0x985,0x885,0xb85,0xa05,0x905,0x805,0xe05)[choice]);pulse()
    write(9);pulse();bits=((read(BASE+36)<<4)&MASK)&~31
    for value in (bits|5,0x3765,bits|21,0x3765,0x2385):write(value);pulse()
    return trace,memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Lodac stock identity')
    targets=struct.unpack_from('<7I',IMAGE.read_bytes(),0x1020a8f4-0x101f6a74)
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe0e8','--stop-address=0xe1f0',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-lodac/bits.disassembly.txt').read_text());cases=0
    for choice,other,level,seed in product(range(8),(0,0xffffff8f),(0,1,2,15,16,31,32,0x80000000,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
        selector=(choice<<4)|other;wanted=oracle(selector,level,seed)
        if execute(old,0xe0e8,selector,level,seed,targets)!=wanted or execute(new,0x10204b5c,selector,level,seed,targets)!=wanted:raise ValueError('Lodac ordered effects mismatch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['All8 selector paths and complete compiled pulse helper executed. Uniform register response model; physical pulse timing and command semantics unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-lodac-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
