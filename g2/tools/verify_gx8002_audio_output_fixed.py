# SPDX-License-Identifier: MIT
"""Decoded fixed output controls, word effects and return values."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_fixed import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,pc,handle,value,seed,getter=False):
    r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=handle,r1=value);saved=r.copy();trace=[];word=seed
    address=0xa0b80010 if getter else 0xa0b00010
    for _ in range(32):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Fixed ABI')
            return r['r0'],trace,word
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='bseti':r[p[0]] |= 1<<int(p[1],0)
        elif op=='and':r[p[0]] &= r[p[1]]
        elif op=='or':r[p[0]] |= r[p[1]]
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Fixed operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a!=address:raise ValueError('Fixed address')
            if op=='ld.w':r[reg]=word;trace.append(('read',a,word))
            else:word=r[reg];trace.append(('write',a,word))
        else:raise ValueError('Fixed instruction '+op)
        pc+=width
    raise ValueError('Fixed instruction bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Fixed stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe268','--stop-address=0xe290',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-fixed/bits.disassembly.txt').read_text());cases=0
    for handle,value,seed in product((0,0x20010000,0xffffffff),(*range(256),0xffff,0x10000,0x10001,0x80000000,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
        first=seed|0x80000000;last=(first&0xff000000)|((value%65536)<<8);a=0xa0b00010
        wanted=(0,[('read',a,seed),('write',a,first),('read',a,first),('write',a,last)],last)
        if execute(old,0xe268,handle,value,seed)!=wanted or execute(new,0x10204cdc,handle,value,seed)!=wanted:raise ValueError('Fixed output effects')
        cases+=1
    getter_cases=0
    for seed in (0,1,0xffffffff,0x80000000,0xa5a5a5a5):
        wanted=(seed,[('read',0xa0b80010,seed)],seed)
        if execute(old,0xe288,0,0,seed,True)!=wanted or execute(new,0x10204cfc,0,0,seed,True)!=wanted:raise ValueError('SDC getter effects')
        getter_cases+=1
    return {'candidate':candidate,'setter_cases':cases,'getter_cases':getter_cases,'source_admitted':False,'hardware_qualified':False,'limits':['Ordered32-bit accesses, unused handle and16-bit truncation checked. Physical register semantics and caller ABI provenance remain to be qualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-fixed-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['setter_cases'],r['getter_cases'])
