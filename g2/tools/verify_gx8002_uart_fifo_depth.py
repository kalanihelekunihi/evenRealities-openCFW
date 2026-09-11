# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_uart_fifo_depth import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,device,parameter,descriptor_base=0x20026a94):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=descriptor_base
    initial=r.copy();memory={descriptor_base+4:device,device+0xf4:parameter};reads=[];pc=entry;condition=False
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('FIFO ABI')
            return r['r0'],reads
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,base,off=m.groups();address=r[base]+int(off,0);r[reg]=memory[address];reads.append((address,r[reg]))
        elif op=='zext':
            high,low=map(int,p[2:]);r[p[0]]=(r[p[1]]>>low)&((1<<(high-low+1))-1)
        elif op in ('lsli','subi','and'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a-b if op=='subi' else a&b)&0xffffffff
        elif op in ('cmpnei','cmplti'):
            value=r[p[0]];value=value if value<0x80000000 else value-0x100000000
            condition=value!=int(p[1],0) if op=='cmpnei' else value<int(p[1],0)
        elif op in ('bt','bf','br','bez','bnez'):
            take=condition if op=='bt' else not condition if op=='bf' else True if op=='br' else r[p[0]]==0 if op=='bez' else r[p[0]]!=0
            if take:following=int(p[-1],0)
        else:raise ValueError('FIFO instruction '+op)
        pc=following
    raise ValueError('FIFO execution bound')

def verify():
    report=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),str(path))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    old=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0xc8ec','--stop-address=0xc954',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-uart-fifo-depth/fifo_depth.disassembly.txt').read_text());cases=0
    expected={1:16,2:32,4:64,8:128,16:256,32:512,64:1024,128:2048}
    for encoding,other,device in product(range(256),(0,0xff00ffff,0xa5001234),(0xa0100000,0xa0200000)):
        parameter=(encoding<<16)|other
        wanted=(expected.get(encoding,0),[(0x20026a98,device),(device+0xf4,parameter)])
        if execute(old,0xc8ec,device,parameter)!=wanted or execute(new,0x10203360,device,parameter)!=wanted:raise ValueError('FIFO stock/source oracle')
        cases+=1
    return {'candidate':report,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['All 256 encoding bytes tested with three unrelated-bit patterns and two device bases. MMIO reads modeled; no physical FIFO behavior qualification.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-uart-fifo-depth-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('FIFO cases:',result['decoded_cases'])
