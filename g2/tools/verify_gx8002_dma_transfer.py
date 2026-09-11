# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_dma_transfer import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,destination,source,length,channel,config,status,changed_base,cache_hook=None):
    state=0x2002e93c;base=0xa1000000;stack=0x2002f000
    memory={state:base,state+872+channel*4:0x20050000,base+0x310:0,base+0x3a0:0,changed_base+0x3a0:0,stack:config,stack-20:0}
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=destination,r1=source,r2=length,r3=channel,r14=stack)
    initial=r.copy();trace=[];pc=entry;saved=None;regs=['r4','r5','r6','r15'];condition=False
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r6, r15' or saved is not None:raise ValueError('Receive frame')
            saved=[r[x] for x in regs];r['r14']-=len(regs)*4
        elif op=='pop':
            if args!='r4-r6, r15' or saved is None:raise ValueError('Receive restore')
            for reg,value in zip(regs,saved):r[reg]=value
            r['r14']+=len(regs)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Receive ABI')
            return r['r0'],trace,{k:v for k,v in memory.items() if k>=stack or k<stack-20}
        elif op in ('mov','movi','lrw'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)
        elif op in ('addu','addi','subi','lsl','lsli','ori','andni'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op in ('addu','addi') else a-b if op=='subi' else a<<b if op in ('lsl','lsli') else a|b if op=='ori' else a&~b)&0xffffffff
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bez','bnez','bhsz'):
            value=r[p[0]]
            if (value==0 if op=='bez' else value!=0 if op=='bnez' else value<0x80000000):jump=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','ldr.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << 2)\)',args)
            if not m:raise ValueError('Receive memory operand')
            reg,base_reg,off=m.groups();addr=(r[base_reg]+(r[off.split()[0]]<<2 if '<<' in off else int(off,0)))&0xffffffff
            if addr not in memory:raise ValueError('Receive memory address')
            if op in ('ld.w','ldr.w'):r[reg]=memory[addr];trace.append(('read',addr,r[reg]))
            else:memory[addr]=r[reg];trace.append(('write',addr,r[reg]))
        elif op=='bsr':
            target=int(args,0)
            target=(target+0x101f6a74)&0xffffffff if entry==0xd104 else target
            if target==0x102038f4:
                trace.append(('configure',r['r0'],r['r1'],r['r2'],r['r3'],memory[r['r14']]))
                result=status
            elif target==0x10025664:
                trace.append(('cache',r['r0'],r['r1']))
                if cache_hook is not None:cache_hook(r['r0'],r['r1'])
                memory[state]=changed_base;result=0xffffffff
            else:raise ValueError('Transfer helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
            r['r0']=result
        else:raise ValueError('Receive instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Receive instruction bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xd104','--stop-address=0xd14c',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-transfer/transfer.disassembly.txt').read_text());cases=0
    for args in product((0,0x20060000),(0,0xa0000000),(0,416,0xffffffff),(0,1),(0,0x20040000),(0,1,0x80000000,0xffffffff),(0xa1000000,0xa1001000)):
        a=execute(old,0xd104,*args);b=execute(new,0x10203b78,*args)
        if a!=b:raise ValueError(('Transfer comparison',args,a,b))
        destination,source,length,channel,config,status,base=args
        if a[0]!=(0xffffffff if status==0xffffffff else 0):raise ValueError('Transfer return')
        calls=[x for x in a[1] if x[0] in ('configure','cache')]
        wanted=[('configure',destination,source,length,channel,config)]
        if status!=0xffffffff:wanted.append(('cache',0x20050000,416))
        if calls!=wanted:raise ValueError('Transfer forwarding')
        writes=[x for x in a[1] if x[0]=='write' and x[1]>=0xa0000000]
        wanted=[] if status==0xffffffff else [('write',0xa1000310,257<<channel),('write',base+0x3a0,257<<channel)]
        if writes!=wanted:raise ValueError('Transfer MMIO oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Initialized channel domain 0/1; configuration and cache modeled. Tests include device-base change across cache boundary. Candidate still exceeds stock envelope.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-transfer-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Transfer cases:',result['decoded_cases'])
