# SPDX-License-Identifier: MIT
"""Decoded word-access and ABI qualification of audio-output bit setters."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_bits import build,ROOT,IMAGE_SHA,sha,Elf32,FUNCTIONS
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,pc,base,value,seed,offset):
    r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=base,r1=value);saved=r.copy();trace=[]
    address=(base+offset)&MASK;word=seed
    for _ in range(24):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')]
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Field ABI')
            return r['r0'],trace,word
        if op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='bclri':r[p[0]] &= ~(1<<int(p[1],0))
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='or':r[p[0]] |= r[p[1]]
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
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Aout stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdf54','--stop-address=0xdf74',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-output-bits/bits.disassembly.txt').read_text());cases=0
    for (name,entry),offset in zip(FUNCTIONS,(8,0)):
        for base,value,seed in product((0xa0a10000,0x20030000,0x1000),(*range(256),0x80000000,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
            address=base+offset;word=(seed&~2)|((value&1)<<1)
            wanted=(base,[('read',address,seed),('write',address,word)],word)
            if execute(old,entry,base,value,seed,offset)!=wanted or execute(new,entry+0x101f6a74,base,value,seed,offset)!=wanted:raise ValueError('Aout effects mismatch')
            cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Word MMIO effects and callee ABI verified with low-bit truncation. Physical register behavior and caller composition remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-bits-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
