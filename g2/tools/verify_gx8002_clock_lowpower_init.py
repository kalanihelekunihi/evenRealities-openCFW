# SPDX-License-Identifier: MIT
"""Decoded low-power initialization routing against independent per-module rules."""
import json,re,subprocess
from itertools import product
from build_gx8002_clock_lowpower_init_candidate import build,ROOT
from analyze_gx8002_upstream_objects import sha,IMAGE_SHA
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,answers,pmu,query_runner=None,set_runner=None,pmu_runner=None):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();pc=entry;condition=False;trace=[]
    for _ in range(800):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            end=int(re.fullmatch(r'r4-r(\d+), r15',args)[1]);saved={f'r{i}':r[f'r{i}'] for i in (*range(4,end+1),15)};r['r14']-=len(saved)*4
        elif op=='pop':
            r.update(saved);r['r14']+=len(saved)*4;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='addi':r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+int(p[-1],0))&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bseti':r[p[0]]=(r[p[1]] if len(p)==3 else r[p[0]])|(1<<int(p[-1],0))
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('br','bt','bf','bnez','bez'):
            if op=='br' or (condition if op=='bt' else not condition if op=='bf' else (r[p[0]]==0)==(op=='bez')):nxt=int(p[-1],0)
        elif op=='ld.w':
            dest,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();assert r[base]+int(off,0)==0xa001008c;r[dest]=pmu_runner() if pmu_runner else pmu;trace.append(('read',r[dest]))
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry<0x100000 else 0);module=r['r0']
            if target==0x10024d70:assert module in answers;result=query_runner(module) if query_runner else answers[module];trace.append(('get',module,result))
            else:assert target==0x10024be0 and 0<=module<26;trace.append(('set',module,r['r1']));result=set_runner(module,r['r1']) if set_runner else 0xffffffff
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')

def expected(answers,pmu):
    trace=[]
    for module in range(26):
        if module in (2,7,8):
            v=answers[module];trace.append(('get',module,v))
            if module==2 and v==1:
                trace.append(('read',pmu))
                if pmu&64:continue
            if module in (7,8):
                if v=={7:3,8:5}[module]:trace.append(('set',module,{7:4,8:6}[module]))
                continue
        trace.append(('set',module,0))
    return trace

def verify():
    candidate=build();p=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(p.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x179b0','--stop-address=0x17a14',str(p)],text=True));new=decode((ROOT/'build/gx8002-board/clock-lowpower-init-candidate.disassembly.txt').read_text());cases=0
    for a,b,c,pmu in product((0,1,2,0xffffffff),(0,3,4,0xffffffff),(0,5,6,0xffffffff),(0,64,0xffffffff,0xffffffbf)):
        answers={2:a,7:b,8:c};assert execute(old,0x179b0,answers,pmu)==execute(new,0x1002599c,answers,pmu)==expected(answers,pmu);cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Decoded full outer routing, conditional PMU read, ordered 26-module rules and integer ABI. Query/set helpers modeled including failing setter return. Nested hardware transitions and size/placement remain outstanding.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-clock-lowpower-init.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
