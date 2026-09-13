# SPDX-License-Identifier: MIT
"""Decode cache initialization ordering and register preservation."""
import json,re,subprocess
from itertools import product
from build_gx8002_cache_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,statuses,seed):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r['r14']=0x20070000
    initial=r.copy();saved=None;pc=entry;trace=[];calls=0
    for _ in range(20):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('Cache initialization frame')
            saved=r['r15'];r['r14']-=4
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('Cache initialization restore')
            r['r15']=saved;r['r14']+=4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Cache initialization ABI')
            if calls!=3:raise ValueError('Cache initialization call count')
            return trace
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='addi':r[p[0]]=(r[p[-2]]+int(p[-1],0) if len(p)==3 else r[p[0]]+int(p[1],0))&0xffffffff
        elif op=='st.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('Cache initialization store operand')
            reg,base,off=match.groups();trace.append(('write',(r[base]+int(off,0))&0xffffffff,r[reg]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xd1cc else 0))&0xffffffff
            if target not in (0x1002571c,0x100255e4,0x100255c4):raise ValueError('Cache initialization helper')
            trace.append(('call',target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xb0000000)+i
            r['r0']=statuses[calls];calls+=1
        else:raise ValueError('Cache initialization instruction '+op)
        pc+=width
    raise ValueError('Cache initialization bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Cache initialization stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd1cc','--stop-address=0xd1ec',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-cache-initialize/initialize.disassembly.txt').read_text())
    wanted=[('call',0x1002571c),('call',0x100255e4),('write',0xe000f014,0x20000023),('call',0x100255c4)]
    cases=0
    for statuses,seed in product(product((0,1,0xffffffff),repeat=3),(0,0x12340000,0xffff0000)):
        if execute(old,0xd1cc,statuses,seed)!=wanted or execute(new,0x10203c40,statuses,seed)!=wanted:raise ValueError('Cache initialization order')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
        'limits':['Helper call ordering, source-encoded region register and ABI checked with caller clobbers. Helper bodies and hardware coherence remain separate qualifications.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-cache-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('Cache initialization cases:',r['decoded_cases'])
