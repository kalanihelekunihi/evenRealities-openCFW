# SPDX-License-Identifier: MIT
"""Decode conditional backup BSS clear and establish callback zeroing when run."""
import json,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,seed):
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};initial=dict(r)
    memory={a:seed for a in range(0x20017090,0x2002d79c,4)}
    pc=0x3ba68;condition=False;saved=None;writes=[]
    for _ in range(100000):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r6';saved=[r[f'r{i}'] for i in (4,5,6)];r['r14']=(r['r14']-12)&0xffffffff
        elif op=='pop':
            assert args=='r4-r6' and saved is not None
            for i,v in zip((4,5,6),saved):r[f'r{i}']=v
            r['r14']=(r['r14']+12)&0xffffffff
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='xor':r[p[0]]^=r[p[1]]
        elif op=='addi':r[p[0]]=(r[p[0]]+int(p[1],0))&0xffffffff
        elif op=='st.w':
            assert args=='r4, (r6, 0x0)' and r['r6'] in memory
            memory[r['r6']]=r['r4'];writes.append(r['r6'])
        elif op=='rts':
            assert r==initial
            assert writes==list(range(0x20017090,0x2002d79c,4))
            assert all(v==0 for v in memory.values())
            return memory
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('clear bound')

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3ba68','--stop-address=0x3ba80',str(p)],text=True))
    for seed in (0,1,0x98765432,0xffffffff):
        memory=execute(code,seed)
        assert [memory[0x200174a8+4*i] for i in range(4)]==[0]*4
    return {'image_sha256':IMAGE_SHA,'clear_sha256':sha(stock[0x3ba68:0x3ba8c]),'cases':4,'cleared_words':(0x2002d79c-0x20017090)//4,'callback_words':4,'source_admitted':False,'limits':['Clear called only on startup branch through0x3bb1e; resume path can skip it.','This establishes zeroing when clear executes, not unconditional startup defaults or callback-table source ownership.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-callback-clear.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'cases;',r['cleared_words'],'words cleared')
