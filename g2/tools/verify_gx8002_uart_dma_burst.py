# SPDX-License-Identifier: MIT
"""Decoded burst lookup against independent enum and ordered-read contracts."""
import json,re,subprocess
from build_gx8002_uart_dma_burst import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,pc,tx,rx,direction,descriptor_address=0x20026a94):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=descriptor_address,r1=direction)
    initial=r.copy();memory={r['r0']+52:tx,r['r0']+56:rx};reads=[];condition=False
    for _ in range(50):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Burst read syntax')
            reg,base,off=m.groups();address=r[base]+int(off,0);r[reg]=memory[address];reads.append((address,r[reg]))
        elif op in ('cmpnei','cmplti','cmphsi'):
            a=r[p[0]];b=int(p[1],0)
            condition=a!=b if op=='cmpnei' else (a if a<0x80000000 else a-0x100000000)<b if op=='cmplti' else a>=b
        elif op in ('inct','incf'):
            if condition==(op=='inct'):r[p[0]]=(r[p[1]]+int(p[2],0))&0xffffffff
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op in ('addu','lsli'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a+b if op=='addu' else a<<b)&0xffffffff
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'):jump=int(args,0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Burst ABI')
            return r['r0'],reads
        else:raise ValueError('Burst instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Burst execution bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xc5dc','--stop-address=0xc650',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-uart-dma-burst/burst.disassembly.txt').read_text());cases=0
    mapping={1<<i:i-1 for i in range(2,11)}
    values=(*range(1026),0x7fffffff,0x80000000,0xffffffff)
    for value in values:
        for tx,rx in ((value,64),(128,value)):
            for direction in (0,1,0x80000000,0xffffffff):
                wanted=(mapping.get(tx if direction else rx,0),[(0x20026ac8,tx),(0x20026acc,rx)])
                if execute(old,0xc5dc,tx,rx,direction)!=wanted or execute(new,0x10203050,tx,rx,direction)!=wanted:raise ValueError(('Burst contract',tx,rx,direction))
                cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Finite burst inputs covering all supported sizes and nearby values; both volatile descriptor reads preserved. No concurrent descriptor mutation proof.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-dma-burst-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Burst cases:',result['decoded_cases'])
