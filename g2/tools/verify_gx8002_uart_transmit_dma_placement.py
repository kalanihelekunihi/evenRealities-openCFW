# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_uart_transmit_dma_placement import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,port,buffer,length,channel,burst1,burst2,status,burst_hook=None,cache_hook=None,cache_buffer=0x20060000,cache_length=77,select_hook=None,callback_hook=None,release_hook=None,helper_addresses=None,descriptor_address=0x20026a94,initial_memory=None,transfer_hook=None):
    descriptor=descriptor_address;base=0xa0000000;stack=0x2002f000
    memory={descriptor:port,descriptor+4:base,descriptor+100:cache_length,descriptor+96:cache_buffer,descriptor+124:0xffffffff}
    if initial_memory is not None:memory=dict(initial_memory)
    memory.update({stack-i:0xdeadbeef for i in range(4,92,4)})
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=descriptor,r1=buffer,r2=length,r14=stack)
    initial=r.copy();trace=[];pc=entry;saved=None;regs=[f'r{i}' for i in range(4,12 if entry==0xc694 else 11)]+['r15'];condition=False;bursts=0
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!=('r4-r11, r15' if entry==0xc694 else 'r4-r10, r15') or saved is not None:raise ValueError('Transmit frame')
            saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if args!=('r4-r11, r15' if entry==0xc694 else 'r4-r10, r15') or saved is None:raise ValueError('Transmit restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Transmit ABI')
            return r['r0'],[x for x in trace if not(x[0] in ('read','write') and stack-88<=x[1]<stack)],{k:v for k,v in memory.items() if k>=stack or k<stack-88}
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subi','lsli','ori','andni'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addu','addi') else a-b if op=='subi' else a<<b if op=='lsli' else a|b if op=='ori' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bez','bnez','bhsz','blz'):
            value=r[p[0]]
            if (value==0 if op=='bez' else value!=0 if op=='bnez' else value>=0x80000000 if op=='blz' else value<0x80000000):jump=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Transmit memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+int(off,0))&0xffffffff
            if addr not in memory:raise ValueError('Transmit memory address')
            if op=='ld.w':r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            target=(target+0x101f6a74)&0xffffffff if entry==0xc694 else target
            if helper_addresses is not None:
                if target not in helper_addresses:raise ValueError('Unmapped relocated DMA helper')
                target=helper_addresses[target]
            if target==0x10025664:
                trace.append(('cache',r['r0'],r['r1']));result=status
                if cache_hook is not None:cache_hook(r['r0'],r['r1'])
            elif target==0x10203a4c:
                trace.append(('select',));result=channel
                if select_hook is not None:result=select_hook()
            elif target==0x10203050:
                trace.append(('burst',r['r0'],r['r1']));result=burst1 if bursts==0 else burst2
                if burst_hook is not None:result=burst_hook(r['r0'],r['r1'],bursts)
                bursts+=1
            elif target==0x10203b64:
                trace.append(('callback',r['r0'],r['r1'],r['r2']));result=status
                if callback_hook is not None:callback_hook(r['r0'],r['r1'],r['r2'])
            elif target==0x10203b38:
                trace.append(('release',r['r0']));result=status
                if release_hook is not None:release_hook(r['r0'])
            elif target==0x10203b78:
                config=memory[r['r14']]
                trace.append(('transfer',r['r0'],r['r1'],r['r2'],r['r3'],tuple(memory[config+i*4] for i in range(12))));result=status
                if transfer_hook is not None:result=transfer_hook(r['r0'],r['r1'],r['r2'],r['r3'],config,tuple(memory[config+i*4] for i in range(12)))
            else:raise ValueError('DMA setup helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=result
        else:raise ValueError('Transmit instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Transmit instruction bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc694','--stop-address=0xc71c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-transmit-dma-placement/dma.disassembly.txt').read_text());cases=0
    for args in product((0,1),(0,0x20050000),(0,32,0xffffffff),(0,3,0x80000000,0xffffffff),(0,9),(1,8),(0,0xffffffff)):
        a=execute(old,0xc694,*args);b=execute(new,0x10203108,*args)
        if a!=b:raise ValueError(('DMA setup mismatch',args,a,b))
        port,buffer,length,channel,first,second,status=args
        if a[0]!=(0xffffffff if channel>=0x80000000 or port>1 else 0):raise ValueError('DMA setup return')
        if channel<0x80000000 and port<=1:
            transfers=[x for x in a[1] if x[0]=='transfer']
            wanted=('transfer',0xa0000000,buffer,length,channel,(0,first,0,0,0,0,second,1,7 if port==0 else 5,1,0,1))
            if transfers!=[wanted]:raise ValueError('DMA config contract')
        calls=[x for x in a[1] if x[0] not in ('read','write')]
        wanted_calls=[('cache',buffer,length),('select',)]
        if channel<0x80000000:
            wanted_calls += [('burst',0x20026a94,1),('burst',0x20026a94,1),
                             ('callback',channel,0x102030c4,0x20026a94),wanted]
        if calls!=wanted_calls:raise ValueError('Transmit DMA independent helper order')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Valid ports only; external ordered accesses and helper argument comparison, excluding private stack layout; called helpers modeled, no DMA hardware behavior claim.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-transmit-dma-placement-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Transmit DMA cases:',result['decoded_cases'])
