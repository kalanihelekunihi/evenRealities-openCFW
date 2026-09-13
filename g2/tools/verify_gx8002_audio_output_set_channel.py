# SPDX-License-Identifier: MIT
"""Decode stock table selection and source conditions with ordered MMIO oracle."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_set_channel import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
REG=0xa0b00014
TABLE=0x1020a9a4

def execute(code,entry,channel,seed):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=0x20010000,r1=channel);saved=r.copy();pc=entry;condition=False;word=seed;trace=[];lookups=[]
    for _ in range(70):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Channel ABI')
            if lookups!=([TABLE+channel,TABLE+4+channel,TABLE+8+channel] if entry==0xe5b8 and channel<4 else []):raise ValueError('Table access sequence')
            return r['r0'],trace,word
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('mvc','mvcv'):r[p[0]]=int(condition if op=='mvc' else not condition)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op=='bez':
            if not r[p[0]]:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('addi','subi'):r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+(1 if op=='addi' else -1)*int(p[-1],0))&0xffffffff
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='nor':r[p[0]]=~(r[p[0]]|r[p[1]])&0xffffffff
        elif op in ('and','or'):r[p[0]]=r[p[0]]&r[p[1]] if op=='and' else r[p[0]]|r[p[1]]
        elif op=='andn':r[p[0]]=r[p[1]]&~r[p[2]]
        elif op in ('andi','andni'):r[p[0]]=r[p[1]]&(int(p[2],0) if op=='andi' else ~int(p[2],0))
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='lrw':
            if int(p[1],0)!=TABLE:raise ValueError('Table literal')
            r[p[0]]=TABLE
        elif op=='ldr.b':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 0\)',args)
            if not m:raise ValueError('Table operand')
            dest,base,index=m.groups();address=r[base]+r[index]
            if not TABLE<=address<TABLE+12:raise ValueError('Table range')
            lookups.append(address);r[dest]=(0,0,1,0,1,0,1,1,0,0,0,1)[address-TABLE]
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,offset=m.groups()
            if r[base]+int(offset,0)!=REG:raise ValueError('Channel MMIO address')
            if op=='ld.w':r[reg]=word;trace.append(('read',REG,word))
            else:word=r[reg];trace.append(('write',REG,word))
        else:raise ValueError('Channel opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Channel bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe5b8','--stop-address=0xe618',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-set-channel/bits.disassembly.txt').read_text());cases=0
    for channel,seed in product(tuple(range(256))+(0x7fffffff,0x80000000,0xfffffffe,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
        left,right,mix={0:(0,1,0),1:(0,0,0),2:(1,1,0),3:(0,1,1)}.get(channel,(0,0,0));word=seed;trace=[]
        for mask,value in ((0xf00,left<<8),(0xf000,right<<12),(1,mix)):
            trace.append(('read',REG,word));word=(word&~mask)|value;trace.append(('write',REG,word))
        wanted=(0,trace,word)
        for code,entry in ((old,0xe5b8),(new,0x1020502c)):
            if execute(code,entry,channel,seed)!=wanted:raise ValueError(('Channel effects',entry,channel,seed))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Ordered register effects and ABI checked. Source removes table dependency; stock table bytes are not reclaimed without a separate reference audit. Physical routing semantics remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-set-channel-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
