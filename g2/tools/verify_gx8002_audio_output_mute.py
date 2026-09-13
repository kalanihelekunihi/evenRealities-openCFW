# SPDX-License-Identifier: MIT
"""Decoded mute control word MMIO and halfword status effects."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_mute import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
def execute(code,pc,handle,value,seed):
    r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=handle,r1=value);saved=r.copy();trace=[];memory={0xa0b00004:seed,0xa0b00014:seed};status=bytearray([0xa5]*4);condition=False
    for _ in range(32):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Fixed ABI')
            return r['r0'],trace,memory,bytes(status)
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='bclri':r[p[0]]=r[p[1]]&~(1<<int(p[2],0)) if len(p)==3 else r[p[0]]&~(1<<int(p[1],0))
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='bseti':r[p[0]] |= 1<<int(p[1],0)
        elif op=='and':r[p[0]] &= r[p[1]]
        elif op=='or':r[p[0]] |= r[p[1]]
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','st.w','st.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Fixed operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='st.h':
                if a!=handle+16:raise ValueError('Mute status address')
                value=r[reg]&65535;status[:2]=value.to_bytes(2,'little');trace.append(('status',a,value))
            elif a not in memory:raise ValueError('Mute MMIO address')
            elif op=='ld.w':r[reg]=memory[a];trace.append(('read',a,r[reg]))
            else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
        else:raise ValueError('Fixed instruction '+op)
        pc+=width
    raise ValueError('Fixed instruction bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Mute stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe618','--stop-address=0xe658',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-mute/bits.disassembly.txt').read_text());cases=0
    for handle,value,seed in product((0x20010000,0x20020004),(*range(256),0x80000000,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
        enabled=int(value!=0);memory={0xa0b00004:seed,0xa0b00014:seed};trace=[]
        for address,bit in ((0xa0b00004,9),(0xa0b00014,11),(0xa0b00014,15)):
            old_word=memory[address];memory[address]=(old_word&~(1<<bit))|(enabled<<bit)
            trace.extend((('read',address,old_word),('write',address,memory[address])))
        trace.append(('status',handle+16,1));wanted=(0,trace,memory,bytes((1,0,0xa5,0xa5)))
        if execute(old,0xe618,handle,value,seed)!=wanted or execute(new,0x1020508c,handle,value,seed)!=wanted:raise ValueError('Mute ordered effects mismatch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Boolean mute and unconditional status1 verified with adjacent status bytes preserved. Valid disjoint RAM handles modeled; physical status meaning remains unresolved.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-mute-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
