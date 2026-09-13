# SPDX-License-Identifier: MIT
"""Decoded standby setter/countdown with independent ordered state oracle."""
import json,re,subprocess,itertools
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
STATE=0x2002e738
MASK=0xffffffff

def execute(code,entry,state,countdown,value):
    regs={f'r{i}':0xabc00000+i for i in range(32)};regs['r0']=value;initial=regs.copy();memory={STATE:state,STATE+4:countdown};trace=[];pc=entry;condition=False
    for _ in range(20):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('lrw','movi'):regs[p[0]]=int(p[1],0)
        elif op=='cmpnei':condition=regs[p[0]]!=int(p[1],0)
        elif op=='subi':regs[p[0]]=(regs[p[0]]-int(p[-1],0))&MASK
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=regs[base]+int(off,0);assert a in memory
            if op=='ld.w':regs[reg]=memory[a];trace.append(('read',a,memory[a]))
            else:memory[a]=regs[reg];trace.append(('write',a,regs[reg]))
        elif op in ('bt','bnez'):
            if condition if op=='bt' else regs[p[0]]!=0:nxt=int(p[-1],0)
        elif op=='rts':
            assert all(regs[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return memory,trace
        else:raise ValueError((op,args))
        pc=nxt
    raise ValueError('standby bound')

def verify():
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA;path=ROOT/'build/gx8002-board/tws-standby-split.elf';elf=Elf32(path.read_bytes(),'standby')
    for name,offset,size in (('.setter',0x183c8,14),('.loop',0x183d8,24)):
        section=next(s for s in elf.sections if s['name']==name);assert section['address']==offset+0x1000dfec and elf.contents(section)==stock[offset:offset+size]
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';analysis=Elf32(wrapper.read_bytes(),'stock');assert analysis.contents(next(s for s in analysis.sections if s['name']=='.data'))==stock
    code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-D','--start-address=0x183c8','--stop-address=0x183f0',str(wrapper)],text=True));cases=0
    for state,count,value in itertools.product((0,1,2,3,4,MASK),(0,1,2,49,50,0x80000000,MASK),(0,1,2,4,MASK)):
        memory={STATE:value,STATE+4:50 if value==2 else count};trace=[('write',STATE,value)]
        if value==2:trace.append(('write',STATE+4,50))
        assert execute(code,0x183c8,state,count,value)==(memory,trace)
        memory={STATE:state,STATE+4:count};trace=[('read',STATE,state)]
        if state==2:
            next_count=(count-1)&MASK;memory[STATE+4]=next_count;trace.extend([('read',STATE+4,count),('write',STATE+4,next_count)])
            if not next_count:memory[STATE]=4;trace.append(('write',STATE,4))
        assert execute(code,0x183d8,state,count,value)==(memory,trace);cases+=2
    memory,_=execute(code,0x183c8,0,0,2)
    for step in range(1,51):
        memory,_=execute(code,0x183d8,memory[STATE],memory[STATE+4],0)
        assert memory=={STATE:2 if step<50 else 4,STATE+4:50-step}
    return {'sequence_steps':50,'elf_sha256':sha(path.read_bytes()),'cases':cases,'source_admitted':False,'limits':['Exact compiled/stock instruction equivalence plus decoded ordered reads/writes and ABI. Finite inputs cover decrement wrap and expiry; no physical concurrency or startup allocation proof. Reproducible builder still pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-tws-standby-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
