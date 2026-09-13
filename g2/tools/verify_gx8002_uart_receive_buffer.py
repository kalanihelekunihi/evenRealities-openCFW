# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_uart_receive_buffer import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,port,buffer,length,callback,private,word,token,dma,dma_result):
    descriptor=(0x20026a94+(port<<7))&0xffffffff;base=0xa0000000+port*0x1000
    memory={descriptor+4:base,descriptor+64:7,descriptor+80:0x1234,descriptor+84:0x5678,base+4:word,base+0xa8:0,descriptor+44:dma,descriptor+88:0,descriptor+92:0,descriptor+96:0,descriptor+100:0,descriptor+104:0,0x2002f000:private}
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=port,r1=buffer,r2=length,r3=callback,r14=0x2002f000)
    initial=r.copy();trace=[];pc=entry;saved=None;regs=['r4','r5','r15']
    for _ in range(60):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args not in ('r4-r5, r15','r4-r6, r15') or saved is not None:raise ValueError('Receive frame')
            frame=args;regs=['r4','r5']+(['r6'] if args=='r4-r6, r15' else [])+['r15']
            saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if saved is None or args!=frame:raise ValueError('Receive restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Receive ABI')
            return r['r0'],trace,memory
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','subi','lsli','ori','andni'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addu' else a-b if op=='subi' else a<<b if op=='lsli' else a|b if op=='ori' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Receive memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+int(off,0))&0xffffffff
            if addr not in memory:raise ValueError('Receive memory address')
            if op=='ld.w':r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            save=target in (0xffe2eaec,0x10025560)
            if target in (0xc71c,0x10203190):
                if (r['r0'],r['r1'],r['r2'])!=(descriptor,buffer,length):raise ValueError('DMA descriptor/buffer/length arguments')
                trace.append(('dma',descriptor,buffer,length));result=dma_result
            elif save:trace.append(('irq_save',));result=token
            elif target in (0xffe2eaf8,0x1002556c):
                if r['r0']!=token:raise ValueError('Receive IRQ token lost')
                trace.append(('irq_restore',token));result=0xffffffff
            else:raise ValueError('Receive buffer helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=result
        else:raise ValueError('Receive instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Receive instruction bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcd0c','--stop-address=0xcd6c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-buffer/buffer.disassembly.txt').read_text());cases=0
    for args in product((0,1),(0,0x20050000),(0,1,32,0xffffffff),(0,0x10207ee0),(0,0x12345678),(0,1,0xffffffff),(0,0x40,0xffffffff),(0,1),(0,0xffffffff)):
        a=execute(old,0xcd0c,*args);b=execute(new,0x10203780,*args)
        if a!=b:raise ValueError(('Receive buffer mismatch',args,a,b))
        port,buffer,length,callback,private,word,token,dma,dma_result=args
        wanted=0xffffffff if not buffer or not callback else dma_result if dma else 0
        if a[0]!=wanted:raise ValueError('Receive buffer return contract')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Finite stock/source ordered access and ABI comparisons; DMA and IRQ leaves modeled. Candidate size is reported by the builder; hardware effects remain unqualified.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-buffer-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Receive buffer cases:',result['decoded_cases'])
