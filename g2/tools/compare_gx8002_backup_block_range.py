#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded leaf block-boundary logic, including output/state aliasing."""
import json,re,subprocess
from build_gx8002_backup_block_range import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=0x20016d60

def execute(code,pc,address,length,index,size,start,end):
    r={f'r{i}':0x12340000+i for i in range(32)}
    initial=r.copy();r.update(r0=address,r1=length,r2=start,r3=end)
    memory={STATE:index&MASK,STATE+4:size,0x30000000:123,0x30000004:456}
    events=[];flag=False
    for _ in range(12000000):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];n=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('lsli','lsri'):
            a=r[p[1]];b=int(p[2],0);r[p[0]]=(a<<b if op=='lsli' else a>>b)&MASK
        elif op=='addu':r[p[0]]=(r[p[1]]+r[p[2]] if len(p)==3 else r[p[0]]+r[p[1]])&MASK
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):n=int(p[1],0)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:n=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            reg,base,offset=m.groups();a=(r[base]+int(offset,0))&MASK
            if op=='ld.w':r[reg]=memory[a];events.append(['read',a,r[reg]])
            else:memory[a]=r[reg];events.append(['write',a,r[reg]])
        elif op in ('addi','subi','andni'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a&~b)&MASK
        elif op in ('and','nor'):
            a=r[p[0]];b=r[p[1]];r[p[0]]=(a&b if op=='and' else ~(a|b))&MASK
        elif op in ('cmpne','cmphs'):flag=r[p[0]]!=r[p[1]] if op=='cmpne' else r[p[0]]>=r[p[1]]
        elif op=='blz':
            if r[p[0]]&0x80000000:n=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (flag if op=='bt' else not flag):n=int(p[0],0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,12)):raise ValueError('saved register')
            return r['r0'],events
        else:raise ValueError('unknown instruction '+op)
        pc=n
    raise ValueError('execution bound')

def expected(address,length,index,size,start,end):
    memory={STATE:index&MASK,STATE+4:size};events=[]
    def write(a,v):memory[a]=v;events.append(['write',a,v])
    def read(a):v=memory[a];events.append(['read',a,v]);return v
    write(start,0)
    if read(STATE)&0x80000000:return address,events
    if address//4096>=read(STATE+4)//4096:return address,events
    write(start,(address//4096)*4096);write(end,0)
    if read(STATE)&0x80000000:return address,events
    capacity=read(STATE+4)
    if capacity//4096==0:return address,events
    last=(address+length-1)&MASK
    if last//4096<capacity//4096:write(end,(last//4096+1)*4096)
    return last,events

def verify():
    from itertools import product
    from build_gx8002_backup_block_range import IMAGE,IMAGE_SHA,sha,Elf32
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x3ff10','--stop-address=0x3ff8c',str(path)],text=True))
    new=decode((ROOT/'build/gx8002-backup-block-range/block-range-linked.disassembly.txt').read_text());cases=0
    for address,length,index,size,(start,end) in product((0,1,4095,4096,8191,8192,MASK),(0,1,4096,MASK),
        (-1,0,1),(0,4095,4096,8192),((0x30000000,0x30000004),(0x30000000,0x30000000),(STATE,STATE+4),(STATE+4,STATE))):
        args=(address,length,index,size,start,end);wanted=expected(*args)
        assert execute(old,0x3ff10,*args)==execute(new,0x100075d0,*args)==wanted
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Ordered output/state aliases and observed return register checked for finite capacities. Caller interpretation of return register, large iteration ranges and hardware remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-block-range-comparison.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
