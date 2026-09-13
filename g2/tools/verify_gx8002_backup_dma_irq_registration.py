# SPDX-License-Identifier: MIT
"""Compose decoded initialization, registration writes, and stock dispatch body."""
import json,re,subprocess
from itertools import product
from verify_gx8002_backup_dma_initialize import execute as initialize
from verify_gx8002_backup_request_irq import execute as register
from build_gx8002_backup_request_irq import build as request_build
from build_gx8002_backup_dma_combined import build,ROOT,Elf32,sha
from analyze_gx8002_upstream_objects import IMAGE,IMAGE_SHA
from verify_gx8002_memcpy_source import decode

def dispatch(code,memory,active):
    r={f'r{i}':0 for i in range(32)};memory=dict(memory);memory[0xe000ec00]=active
    pc=0x3d1d2;calls=[]
    for _ in range(24):
        if pc==0x3d1f0:return calls
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];nxt=pc+width
        if op=='lrw':r[p[0]]=int(p[1],0)
        elif op in ('andi','subi','lsli','addu'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a&b if op=='andi' else a-b if op=='subi' else a<<b if op=='lsli' else a+b)&0xffffffff
        elif op in ('ld.w','ldr.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if m:
                reg,base,index,shift=m.groups();address=r[base]+(r[index]<<int(shift))
            else:
                m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
                reg,base,offset=m.groups();address=r[base]+int(offset,0)
            r[reg]=memory[address&0xffffffff]
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='jsr':calls.append((r[args],r['r0'],r['r1']))
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('dispatch bound')

def verify():
    combined=build();request=request_build()
    init=decode((ROOT/'build/gx8002-backup-dma-combined/combined.disassembly.txt').read_text())
    reg=decode((ROOT/'build/gx8002-backup-request-irq/request.disassembly.txt').read_text())
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    p=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(p.read_bytes(),str(p));assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3d1d2','--stop-address=0x3d1f0',str(p)],text=True))
    cases=0
    for seed,base,status in product((0,0xffffffff,0x12345678),(0xa1000000,0xa1001000),(0,1,0xffffffff)):
        writes=[]
        def hook(irq,handler,context):writes.extend(register(reg,0x10004844,irq,handler,context))
        initialize(init,0x10004d14,seed,base,status,state=0x2002d3e8,gate=0x10003be8,request_irq=0x10004844,irq_hook=hook)
        assert writes==[(0x200173f8,0x10004c08),(0x200173fc,0),(0xe000e100,1024)]
        memory=dict(writes)
        for active in (42,0xfffffe2a):
            assert dispatch(code,memory,active)==[(0x10004c08,10,0)];cases+=1
        memory[0x200173f8]=0
        assert dispatch(code,memory,42)==[];cases+=1
    return {'combined':combined,'request':request,'dispatch_body_sha256':sha(stock[0x3d1d2:0x3d1f0]),'cases':cases,'source_admitted':False,'limits':['Dispatch body only: hardware interrupt save/restore and IRQ arrival excluded.','Initialization and registration decoded; dispatch target observed, DMA handler body separately qualified. External reference closure remains separate.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-dma-irq-registration.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'composition cases passed')
