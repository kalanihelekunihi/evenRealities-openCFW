# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_audio_rough_gain import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,source,left,right,seed):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=source,r1=left,r2=right)
    initial=r.copy();memory={0xa0a00000+off:seed^off for off in (0xc,0x28,0x2c,0x48,0x4c)};trace=[];pc=entry;condition=False
    for _ in range(50):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Channel ABI')
            return r['r0'],trace,memory
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op=='ins':
            high,low=int(p[2],0),int(p[3],0);mask=((1<<(high-low+1))-1)<<low;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<low)&mask)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Channel operand')
            reg,base,offset=m.groups();address=(r[base]+int(offset,0))&0xffffffff
            if address not in memory:raise ValueError('Channel MMIO address')
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        else:raise ValueError('Channel instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Channel bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Channel stock wrapper')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd938','--stop-address=0xd988',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-audio-rough-gain/gain.disassembly.txt').read_text());cases=0
    for source,left,seed in product((0,1,2,3,4,5,6,7,8,0x80000000,0xffffffff),(*range(256),0x80000000,0xffffffff),(0,0xa5a5a5a5,0xffffffff)):
        right=0
        memory={0xa0a00000+off:seed^off for off in (0xc,0x28,0x2c,0x48,0x4c)};trace=[]
        for off in {1:(0xc,),2:(0x28,0x2c),4:(0x48,0x4c)}.get(source,()):
            address=0xa0a00000+off
            trace.append(('read',address,memory[address]));memory[address]=(memory[address]&~240)|((left&15)<<4);trace.append(('write',address,memory[address]))
        wanted=(0,trace,memory)
        if execute(old,0xd938,source,left,right,seed)!=wanted or execute(new,0x102043ac,source,left,right,seed)!=wanted:raise ValueError('Channel selector oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Exact source selectors and no-op combinations, low-four-bit gain narrowing, ordered stereo writes and unrelated-bit preservation checked. MMIO modeled; physical gain response unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-rough-gain-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Channel cases:',r['decoded_cases'])
