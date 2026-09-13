# SPDX-License-Identifier: MIT
"""Qualify ordered buffer programming and modeled cache-call mutation."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_config_buffer import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
CONFIG=0x20020000
BASE=0xa0b80000

def execute(code,entry,config,mutation):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=0x20010000,r1=CONFIG,r14=0x20070000);saved=r.copy();stack={};trace=[];state=list(config);memory={BASE+4:0x11111111,BASE+8:0x22222222,BASE+12:0x33333333};pc=entry;names=None;calls=0
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args not in ('r4-r5, r15','r4-r6, r15'):raise ValueError('Buffer frame')
            names=('r4','r5','r15') if args=='r4-r5, r15' else ('r4','r5','r6','r15');r['r14']-=4*len(names)
            for i,name in enumerate(names):stack[r['r14']+4*i]=r[name]
        elif op in ('pop','rts'):
            if op=='pop':
                if args!=('r4-r5, r15' if len(names)==3 else 'r4-r6, r15'):raise ValueError('Buffer restore')
                for i,name in enumerate(names):r[name]=stack[r['r14']+4*i]
                r['r14']+=4*len(names)
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Buffer ABI')
            return r['r0'],trace,memory,state
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='addu':r[p[0]]=((r[p[1]]+r[p[2]]) if len(p)==3 else (r[p[0]]+r[p[1]]))&0xffffffff
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Buffer operand')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w':
                if address not in (CONFIG,CONFIG+4,CONFIG+8):raise ValueError('Buffer config address')
                r[reg]=state[(address-CONFIG)//4];trace.append(('config_read',address-CONFIG,r[reg]))
            else:
                if address not in memory:raise ValueError('Buffer MMIO address')
                memory[address]=r[reg];trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe3f8 else 0))&0xffffffff
            if target!=0x10025664:raise ValueError('Buffer cache target')
            trace.append(('cache_clean',r['r0'],r['r1']));calls+=1
            if mutation:
                if calls==1:state[1]=mutation[0]
                state[2]=(state[2]+mutation[1])&0xffffffff
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Buffer instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Buffer execution bound')

def oracle(config,mutation):
    state=list(config);trace=[('config_read',0,state[0])];memory={BASE+4:0x11111111,BASE+8:0x22222222,BASE+12:0x33333333}
    if not state[0] or state[0]&15:return 0xffffffff,trace,memory,state
    memory[BASE+4]=(state[0]+0xe0000000)&0xffffffff
    trace.extend((('write',BASE+4,memory[BASE+4]),('config_read',8,state[2]),('cache_clean',state[0],state[2])))
    if mutation:state[1]=mutation[0];state[2]=(state[2]+mutation[1])&0xffffffff
    trace.append(('config_read',4,state[1]))
    if state[1]:
        if state[1]&15:return 0xffffffff,trace,memory,state
        memory[BASE+8]=(state[1]+0xe0000000)&0xffffffff
        trace.extend((('write',BASE+8,memory[BASE+8]),('config_read',8,state[2]),('cache_clean',state[1],state[2])))
        if mutation:state[2]=(state[2]+mutation[1])&0xffffffff
    trace.extend((('config_read',8,state[2]),('write',BASE+12,state[2])));memory[BASE+12]=state[2]
    return 0,trace,memory,state

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Buffer stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe3f8','--stop-address=0xe44c',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-config-buffer/bits.disassembly.txt').read_text());cases=0
    addresses=tuple(range(32))+(0x20000000,0x20000100,0x80000000,0xfffffff0,0xffffffff)
    for first,second,length,mutation in product(addresses,addresses,(0,1,16,0x7fffffff,0xffffffff),(None,(0,1),(0x20000200,0xffffffff),(0x20000201,16))):
        config=(first,second,length);wanted=oracle(config,mutation)
        for code,entry in ((old,0xe3f8),(new,0x10204e6c)):
            if execute(code,entry,config,mutation)!=wanted:raise ValueError(('Buffer effects',entry,config,mutation))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Readable disjoint 12-byte config. Cache clean is modeled with caller clobbers and optional mutation of later config fields; physical cache operation and buffer address validity are not qualified. Null config is unguarded in stock.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-config-buffer-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
