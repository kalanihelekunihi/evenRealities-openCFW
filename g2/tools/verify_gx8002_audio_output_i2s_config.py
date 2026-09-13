# SPDX-License-Identifier: MIT
"""Strict decoded DAC config access widths, ordering and independent effects."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_i2s_config import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
BASE=0xa0a10000
CONFIG=0x20030000
FIELDS=((4,24,4,16,1),(4,28,4,15,1),(4,32,4,14,1),(4,4,4,9,1),(4,8,4,4,3),(4,12,4,2,2),(4,16,4,0,2),(16,36,4,31,1))
def execute(code,pc,config,seed,base=BASE,config_address=CONFIG):
    r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=base,r1=config_address);saved=r.copy()
    memory={base+off:seed for off in (4,16)};trace=[]
    for _ in range(160):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')]
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('DAC ABI')
            return trace,memory
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='bclri':r[p[0]]=r[p[1]]&~(1<<int(p[2],0)) if len(p)==3 else r[p[0]]&~(1<<int(p[1],0))
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='and':r[p[0]] &= r[p[1]]
        elif op=='or':r[p[0]] |= r[p[1]]
        elif op in ('zextb','zexth'):r[p[0]]=r[p[1]]&((1<<(8 if op=='zextb' else 16))-1)
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('ld.w','ld.h','ld.b','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('DAC operand')
            reg,base,off=m.groups();a=(r[base]+int(off,0))&MASK;size={'w':4,'h':2,'b':1}[op[-1]]
            if a in memory:
                if size!=4:raise ValueError('Narrow DAC MMIO')
                if op=='st.w':memory[a]=r[reg];trace.append(('write',a,r[reg]))
                else:r[reg]=memory[a];trace.append(('read',a,r[reg]))
            elif config_address<=a and a+size<=config_address+40 and op.startswith('ld'):
                r[reg]=int.from_bytes(config[a-config_address:a-config_address+size],'little');trace.append(('config',a,size,r[reg]))
            else:raise ValueError('DAC memory access')
        else:raise ValueError('DAC instruction '+op)
        pc+=width
    raise ValueError('DAC bound')
def oracle(config,seed):
    memory={BASE+off:seed for off in (4,16)};trace=[]
    for reg,offset,size,shift,bits in FIELDS:
        a=BASE+reg;old=memory[a];value=int.from_bytes(config[offset:offset+size],'little');mask=((1<<bits)-1)<<shift
        memory[a]=(old&~mask)|((value<<shift)&mask)
        trace.extend((('read',a,old),('config',CONFIG+offset,size,value),('write',a,memory[a])))
    old=memory[BASE+16];memory[BASE+16]=(old&0xff000000)|1024
    trace.extend((('read',BASE+16,old),('write',BASE+16,memory[BASE+16])))
    return trace,memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('DAC stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xe03c','--stop-address=0xe0e8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-i2s-config/bits.disassembly.txt').read_text());cases=0
    for byte,value,seed in product(range(40),(0,1,2,3,7,8,127,128,254,255),(0,0xffffffff,0xa5a5a5a5)):
        config=bytearray((i*17+53)&255 for i in range(40));config[byte]=value;wanted=oracle(config,seed)
        if execute(old,0xe03c,config,seed)!=wanted or execute(new,0x10204ab0,config,seed)!=wanted:raise ValueError('DAC ordered effects mismatch '+repr((byte,value,seed)))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['All40 configuration bytes including padding varied independently at boundary values. Ordered configuration read widths andnine word RMWs checked. Extra field semantics and physical caller composition remain unresolved.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-i2s-config-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
