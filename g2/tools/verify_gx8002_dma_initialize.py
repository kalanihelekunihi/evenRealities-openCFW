# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_dma_initialize import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,seed,changed_base,status,state=0x2002e93c,gate=0x10025080,request_irq=0x1002553c,gate_hook=None,irq_hook=None):
    memory={state+i:seed for i in (0,4,0x368,0x36c,0x370,0x371)}
    for base in (0xa1000000,changed_base):memory.update({base+i:seed for i in (0x398,0x338,0x340,0x348,0x350,0x358)})
    r={f'r{i}':(seed+i)&0xffffffff for i in range(32)};r['r14']=0x2002f000
    initial=r.copy();trace=[];pc=entry;saved=None;regs=['r4','r15']
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Receive frame')
            saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Receive restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Receive ABI')
            return trace,memory
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subi','lsli','ori','andni','and'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addu','addi') else a-b if op=='subi' else a<<b if op=='lsli' else a|b if op=='ori' else a&b if op=='and' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Receive memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+int(off,0))&0xffffffff
            if addr not in memory:raise ValueError('Receive memory address')
            if op=='ld.w':r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            if entry==0xd14c:target=(target+0x101f6a74)&0xffffffff
            if target==gate:
                trace.append(('gate',r['r0'],r['r1']))
                if gate_hook is not None:gate_hook(r['r0'],r['r1'])
                if r['r1']==1:memory[state]=changed_base
            elif target==request_irq:
                trace.append(('irq',r['r0'],r['r1'],r['r2']))
                if irq_hook is not None:irq_hook(r['r0'],r['r1'],r['r2'])
            else:raise ValueError('Initializer helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=status
        else:raise ValueError('Receive instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Receive instruction bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd14c','--stop-address=0xd1cc',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-initialize/initialize.disassembly.txt').read_text());cases=0
    for seed,base,status in product((0,0xffffffff,0x12345678),(0xa1000000,0xa1001000),(0,1,0xffffffff)):
        a=execute(old,0xd14c,seed,base,status);b=execute(new,0x10203bc0,seed,base,status)
        if a!=b:raise ValueError('Initializer stock/source')
        s=0x2002e93c
        wanted=[('write',s,0xa1000000),('write',s+4,2),('write',s+0x368,(s+23)&~15),('write',s+0x370,0),('write',s+0x36c,(s+455)&~15),('write',s+0x371,0),('gate',25,1),('read',s,base),('write',base+0x398,0)]
        wanted += [('write',base+o,0xffffffff) for o in (0x338,0x340,0x348,0x350,0x358)]
        wanted += [('write',base+0x398,1),('gate',25,0),('irq',10,0x10203adc,0)]
        if a[0]!=wanted:raise ValueError('Initializer independent order')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Clock/IRQ helpers modeled with caller clobbers and controlled state-base mutation. No hardware reset/IRQ delivery proof.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-initialize-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Initializer cases:',result['decoded_cases'])
