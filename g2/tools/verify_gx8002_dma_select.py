# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_dma_select import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,allocation,token,gate_hook=None,state_address=0x2002e93c,helper_addresses=None,irq_hook=None):
    memory={state_address+4:len(allocation)}
    memory.update({state_address+880+i:value for i,value in enumerate(allocation)})
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x2002f000
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
            return r['r0'],trace,memory
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subi','lsli','ori','andni'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addu','addi') else a-b if op=='subi' else a<<b if op=='lsli' else a|b if op=='ori' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='bt':
            if condition:jump=int(args,0)
        elif op=='bnez':
            if r[p[0]]!=0:jump=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Receive memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+int(off,0))&0xffffffff
            if addr not in memory:raise ValueError('Receive memory address')
            if op in ('ld.w','ld.b'):r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            if helper_addresses is not None:
                if target not in helper_addresses:raise ValueError('Relocated selection helper')
                target=helper_addresses[target]
            save=target in (0xffe2eaec,0x10025560)
            if save:
                if irq_hook is not None and irq_hook(True,r['r0'])!=token:raise ValueError('Selection decoded token')
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


def expected(allocation,token):
    memory={0x2002e940:len(allocation),**{0x2002ecac+i:v for i,v in enumerate(allocation)}}
    trace=[('irq_save',),('read',0x2002e940,len(allocation))];result=0xffffffff
    for i,value in enumerate(allocation):
        trace.append(('read',0x2002ecac+i,value))
        if value==0:
            result=i;memory[0x2002ecac+i]=1
            trace.extend([('write',0x2002ecac+i,1),('resource',25,1)]);break
    trace.append(('irq_restore',token))
    return result,trace,memory


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcfd8','--stop-address=0xd024',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-select/select.disassembly.txt').read_text());cases=0
    for count in range(9):
        for bits in range(1<<count):
            for occupied in (1,128,255):
                allocation=[occupied if bits&(1<<i) else 0 for i in range(count)]
                for token in (0,0x40,0x80000000,0xffffffff):
                    wanted=expected(allocation,token)
                    if execute(old,0xcfd8,allocation,token)!=wanted or execute(new,0x10203a4c,allocation,token)!=wanted:raise ValueError(('Selection contract',allocation,token))
                    cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['All allocation occupancy combinations for counts 0 through 8; this is a test domain, not established hardware capacity. IRQ/resource helpers modeled.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-select-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Selection cases:',result['decoded_cases'])
