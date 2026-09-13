# SPDX-License-Identifier: MIT
"""Decoded backup registration writes and guard checks."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_request_irq import build,ROOT,Elf32,IMAGE,IMAGE_SHA,sha
from verify_gx8002_memcpy_source import decode

def execute(code,entry,irq,handler,context):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=irq,r1=handler,r2=context)
    initial=dict(r);pc=entry;condition=False;trace=[]
    for _ in range(30):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return trace
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op in ('addu','lsli','lsl'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addu' else a<<b)&0xffffffff
        elif op in ('str.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if m:
                reg,base,index,shift=m.groups();address=r[base]+(r[index]<<int(shift))
            else:
                m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
                reg,base,offset=m.groups();address=r[base]+int(offset,0)
            trace.append((address&0xffffffff,r[reg]))
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('instruction bound')

def verify():
    candidate=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper));assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x3d184','--stop-address=0x3d1a4',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-request-irq/request.disassembly.txt').read_text());cases=0
    for irq,handler,context in product((*range(34),0x80000000,0xffffffff),(0,0x10004c04,0x10004c08),(0,0x12345678,0xffffffff)):
        a=execute(old,0x3d184,irq,handler,context);b=execute(new,0x10004844,irq,handler,context)
        wanted=[] if irq>=32 or not handler else [(0x200173a8+irq*8,handler),(0x200173ac+irq*8,context),(0xe000e100,1<<irq)]
        assert a==b==wanted;cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Ordered stores and guards checked; hardware enable effects and asynchronous dispatch not modeled.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-backup-request-irq-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'],'cases passed')
