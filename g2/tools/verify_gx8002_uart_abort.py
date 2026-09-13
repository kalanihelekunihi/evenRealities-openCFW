# SPDX-License-Identifier: MIT
"""Decode UART abort wrappers through channel abort, preserving shared descriptors."""
import json,re,subprocess
from itertools import product
from build_gx8002_uart_abort import build,ROOT,IMAGE_SHA,sha,Elf32
from build_gx8002_dma_abort import build as build_dma
from verify_gx8002_dma_abort import execute as abort
from verify_gx8002_memcpy_source import decode


def execute(code,entry,argument,memory,hook):
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=argument,r14=0x20070000)
    initial=r.copy();saved=None;pc=entry;trace=[]
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args not in ('r15','r4, r15') or saved is not None:raise ValueError('UART abort frame')
            frame=args;regs=['r15'] if args=='r15' else ['r4','r15'];saved=[r[x] for x in regs];r['r14']-=4*len(regs)
        elif op=='pop':
            if saved is None or args!=frame:raise ValueError('UART abort restore')
            for name,value in zip(regs,saved):r[name]=value
            r['r14']+=4*len(regs)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('UART abort ABI')
            return r['r0'],trace
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','lsli','subi'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addu' else a<<b if op=='lsli' else a-b)&0xffffffff
        elif op in ('bez','blz'):
            if r[p[0]]==0 if op=='bez' else r[p[0]]>=0x80000000:jump=int(p[1],0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('UART abort memory operand')
            reg,pointer,offset=match.groups();address=(r[pointer]+int(offset,0))&0xffffffff
            if address not in memory:raise ValueError('UART abort memory bounds')
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        elif op=='bsr':
            target=int(args,0)+(0x101f6a74 if entry<0x10000000 else 0)
            trace.append(('call',target,r['r0']));result,nested=hook(target,r['r0']);trace.extend(nested)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=result
        else:raise ValueError('UART abort instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('UART abort bound')


def verify():
    candidate=build();dependency=build_dma();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('UART abort stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc7a8','--stop-address=0xd0f0',str(wrapper)],text=True));new={}
    for item in candidate['functions']:
        kind=item['symbol'].removeprefix('open_cfw_gx8002_uart_')
        new.update(decode((ROOT/f'build/gx8002-uart-abort/{kind}.disassembly.txt').read_text()))
    new.update(decode((ROOT/'build/gx8002-dma-abort/abort.disassembly.txt').read_text()))
    cases=0
    for receive,port,mode,channel,status in product((False,True),(0,1),(0,1,0xffffffff),(0,1,0x80000000,0xffffffff),(0,1,0xffffffff)):
        descriptor=0x20026a94+port*128;slot=descriptor+(104 if receive else 124)
        inner=0xc7c0 if receive else 0xc7a8;outer=0xcc90 if receive else 0xcc74
        wanted=[('read',descriptor+44,mode)]
        initial={descriptor+44:mode,slot:channel};expected=dict(initial)
        if mode:
            wanted.extend([('call',inner+0x101f6a74,descriptor),('read',slot,channel)])
            if channel<0x80000000:
                wanted.extend([('call',0x10203b40,channel),('read',0x2002e93c,0xa1000000),('write',0xa10003a0,256<<channel),('clear',channel),('deallocate',channel),('write',slot,0xffffffff)])
                expected[slot]=0xffffffff
        for code,delta in ((old,0),(new,0x101f6a74)):
            memory=dict(initial)
            def hook(target,argument):
                if target==inner+0x101f6a74:return execute(code,inner+delta,argument,memory,hook)
                if target==0x10203b40:return abort(code,0xd0cc+delta,argument,0xa1000000,status)
                raise ValueError('UART abort call target')
            result=execute(code,outer+delta,port,memory,hook)
            if result!=(0,wanted) or memory!=expected:raise ValueError('UART abort nested contract')
        cases+=1
    return {'candidate':candidate,'dma_dependency':dependency,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
        'limits':['Valid ports 0/1, DMA channels 0/1 and signed sentinel channels checked. Nested wrappers and DMA abort execute separate frames; DMA clear/deallocate bodies modeled. Physical abort and concurrency unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-uart-abort-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('UART abort cases:',r['decoded_cases'])
