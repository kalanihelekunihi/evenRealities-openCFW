# SPDX-License-Identifier: MIT
"""Decode and compare indexed audio field address, word accesses and ABI."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_channel_field import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,pc,index,value,seed):
    r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=index,r1=value);saved=r.copy();trace=[]
    address=(0xa0a00000+(((index+10)&MASK)<<2))&MASK;word=seed
    for _ in range(24):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')]
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Field ABI')
            return r['r0'],trace,word
        if op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo
            r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w','ldr.w','str.w'):
            if op in ('ldr.w','str.w'):
                m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args)
                if not m:raise ValueError('Indexed word operand')
                reg,base,idx=m.groups();a=(r[base]+(r[idx]<<2))&MASK
            else:
                m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
                if not m:raise ValueError('Word operand')
                reg,base,off=m.groups();a=(r[base]+int(off,0))&MASK
            if a!=address:raise ValueError('Field address mismatch')
            if op.startswith('ld'):r[reg]=word;trace.append(('read',a,word))
            else:word=r[reg];trace.append(('write',a,word))
        else:raise ValueError('Field instruction '+op)
        pc+=width
    raise ValueError('Field instruction bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Field stock wrapper identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdf3c','--stop-address=0xdf54',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-channel-field/field.disassembly.txt').read_text());cases=0
    for index,value,seed in product((*range(16),0x3ffffff5,0x3ffffff6,0x40000000,0x7fffffff,0xfffffff5,0xfffffff6,0xffffffff),(*range(128),0x80000000,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
        address=(0xa0a00028+4*index)&MASK;word=(seed&~0xfc00)|((value%64)<<10)
        wanted=(0,[('read',address,seed),('write',address,word)],word)
        if execute(old,0xdf3c,index,value,seed)!=wanted or execute(new,0x102049b0,index,value,seed)!=wanted:raise ValueError('Field independent effects mismatch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Arithmetic address wrapping tested as decoded behavior; valid hardware index domain and semantic API name unresolved. No source admission yet.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-channel-field-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
