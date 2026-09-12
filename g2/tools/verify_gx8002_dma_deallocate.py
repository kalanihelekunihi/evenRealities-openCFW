# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_dma_deallocate import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,allocation,token,channel,gate_hook=None,irq_hook=None):
    memory={0x2002e940:len(allocation)}
    memory.update({0x2002ecac+i:value for i,value in enumerate(allocation)})
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x2002f000;r['r0']=channel
    initial=r.copy();trace=[];pc=entry;saved=None;regs=['r4','r5','r15'];condition=False
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r5, r15' or saved is not None:raise ValueError('Receive frame')
            saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None:raise ValueError('Receive restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Receive ABI')
            return trace,memory
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subi','lsli','ori','andni'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addu','addi') else a-b if op=='subi' else a<<b if op=='lsli' else a|b if op=='ori' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='bnez':
            if r[p[0]]!=0:jump=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='br':jump=int(args,0)
        elif op=='ldbi.b':
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args)
            if not m:raise ValueError('Postincrement byte operand')
            reg,base_reg=m.groups();addr=r[base_reg]
            if addr not in memory:raise ValueError('Postincrement byte address')
            r[reg]=memory[addr]&255;trace.append(('read',addr,r[reg]))
            r[base_reg]=(addr+1)&0xffffffff
        elif op in ('ld.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Receive memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+int(off,0))&0xffffffff
            if addr not in memory:raise ValueError('Receive memory address')
            if op in ('ld.w','ld.b'):r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            save=target in (0xffe2eaec,0x10025560)
            if save:
                if irq_hook is not None and irq_hook(True,r['r0'])!=token:raise ValueError('Deallocation IRQ save result')
                trace.append(('irq_save',))
            elif target in (0xffe2eaf8,0x1002556c):
                if r['r0']!=token:raise ValueError('Selection IRQ token')
                if irq_hook is not None:irq_hook(False,r['r0'])
                trace.append(('irq_restore',token))
            elif target in (0xffe2e60c,0x10025080):
                trace.append(('resource',r['r0'],r['r1']))
                if gate_hook is not None:gate_hook(r['r0'],r['r1'])
            else:raise ValueError('Selection helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=token if save else 0xffffffff
        else:raise ValueError('Receive instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Receive instruction bound')


def expected(allocation,token,channel):
    values=list(allocation);values[channel]=0
    memory={0x2002e940:len(values),**{0x2002ecac+i:v for i,v in enumerate(values)}}
    trace=[('irq_save',),('write',0x2002ecac+channel,0),('read',0x2002e940,len(values))]
    for i,value in enumerate(values):
        trace.append(('read',0x2002ecac+i,value))
        if value==1:break
    else:trace.append(('resource',25,0))
    trace.append(('irq_restore',token))
    return trace,memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd024','--stop-address=0xd068',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-deallocate/deallocate.disassembly.txt').read_text());cases=0
    for count in range(1,5):
        for allocation in product((0,1,2,255),repeat=count):
            for channel,token in product(range(count),(0,0x40,0x80000000,0xffffffff)):
                wanted=expected(allocation,token,channel)
                if execute(old,0xd024,allocation,token,channel)!=wanted or execute(new,0x10203a98,allocation,token,channel)!=wanted:raise ValueError('Deallocation contract')
                cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Counts 1..4, valid in-table channel; initialized hardware uses two. IRQ/clock modeled, no concurrency proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-dma-deallocate-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Deallocation cases:',report['decoded_cases'])
