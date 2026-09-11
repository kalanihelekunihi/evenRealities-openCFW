# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_uart_receive_complete import build,ROOT
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE_SHA,sha
from build_transparent_image import Elf32


def execute(code,entry,channel,port,buffer,length,callback,private,mutate,release_hook=None,cache_hook=None,descriptor=0x20026a94):
    memory={descriptor+104:channel,descriptor:port,descriptor+96:buffer,descriptor+100:length,descriptor+88:callback,descriptor+92:private}
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=descriptor,r14=0x2002f000)
    initial=r.copy();trace=[];pc=entry;saved=None;regs=['r4','r15']
    for _ in range(60):
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
        elif op in ('bsr','jsr'):
            if op=='jsr':
                trace.append(('callback',r[args],r['r0'],r['r1']))
            else:
                target=int(args,0)
                if entry==0xc670:target=(target+0x101f6a74)&0xffffffff
                if target==0x10203b38:
                    trace.append(('release',r['r0']))
                    if release_hook is not None:release_hook(r['r0'])
                    if mutate:memory[descriptor+96]=0x20060000;memory[descriptor+100]=128
                elif target==0x100256c0:
                    trace.append(('cache',r['r0'],r['r1']))
                    if cache_hook is not None:cache_hook(r['r0'],r['r1'])
                    if mutate:memory[descriptor+88]=0x10208098;memory[descriptor+92]=0xabcdef01;memory[descriptor]=1
                else:raise ValueError('Completion helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Receive instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Receive instruction bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc670','--stop-address=0xc694',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-receive-complete/complete.disassembly.txt').read_text());cases=0
    for args in product((0,1,0xffffffff),(0,1),(0x20050000,0xfffffff0),(0,77,0xffffffff),(0x10207ee0,0x10208098),(0,0x12345678),(False,True)):
        a=execute(old,0xc670,*args);b=execute(new,0x102030e4,*args)
        if a!=b:raise ValueError('Completion stock/source mismatch')
        channel,port,buffer,length,callback,private,mutate=args
        if mutate:buffer,length,callback,private,port=0x20060000,128,0x10208098,0xabcdef01,1
        d=0x20026a94
        wanted=[('read',d+104,channel),('release',channel),('write',d+104,0xffffffff),('read',d+100,length),('read',d+96,buffer),('cache',buffer,length),('read',d+88,callback),('read',d+92,private),('read',d,port),('callback',callback,port,private)]
        if a[0]!=wanted:raise ValueError('Completion independent order')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Modeled release/cache/callback calls with caller clobbers and controlled descriptor mutation. No physical completion delivery proof.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-receive-complete-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Completion cases:',result['decoded_cases'])
