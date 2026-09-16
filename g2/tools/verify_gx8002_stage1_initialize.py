# SPDX-License-Identifier: MIT
"""Execute dispatcher against stock with helper-driven state changes."""
import json,re,subprocess
from itertools import product
from build_gx8002_stage1_initialize import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,mapping,state,updates,seed,state_runner=None):
    r={f'r{i}':(seed+i*0x10203)&0xffffffff for i in range(32)};initial=dict(r);saved=None;pc=entry;condition=False;trace=[]
    for _ in range(40):
        op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r15';saved=r['r15'];r['r14']=(r['r14']-4)&0xffffffff
        elif op=='pop':
            assert args=='r15';r['r15']=saved;r['r14']=(r['r14']+4)&0xffffffff
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();assert r[base]+int(off,0)==0x20001720
            r[reg]=state;trace.append(['read_state',state])
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='bsr':
            name=mapping[int(args,0)];event=['call',name]
            if name==0x39c34:event.extend([r['r0'],r['r1']])
            trace.append(event)
            if name==0x39678 and state_runner is not None:
                effects=state_runner();trace.extend(effects)
                for effect in effects:
                    if effect[:2]==['write',0x20001720]:state=effect[2]
            if name in updates:state=updates[name]
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xdead0000^i)&0xffffffff
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('dispatcher bound')


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x39744','--stop-address=0x39774',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-stage1-initialize/initialize.disassembly.txt').read_text())
    helpers=(0x39678,0x39c44,0x3912c,0x38a88,0x39c34);mapping={a:a for a in (*helpers,0x396a0)}
    runtime=lambda a:a-0x38954+0x10000000
    mapped={runtime(a):a for a in mapping};cases=0
    for state,changed,final,seed in product((0,1,2,3,0xffffffff),(None,*helpers),(0,2,0xffffffff),(0,0x87654321)):
        updates={} if changed is None else {changed:final}
        a=execute(old,0x39744,mapping,state,updates,seed);b=execute(new,runtime(0x39744),mapped,state,updates,seed)
        expected_state=state if changed is None else final
        expected=[['call',h]+([1,0] if h==0x39c34 else []) for h in helpers]+[['read_state',expected_state]]+([['call',0x396a0]] if expected_state==2 else [])
        assert a==b==expected;cases+=1
    from verify_gx8002_stage1_boot_state import execute as run_state
    state_old=decode(subprocess.check_output([tool,'-D','--start-address=0x39678','--stop-address=0x396a0',str(wrapper)],text=True))
    composed_cases=0
    for state,first,second,seed in product((0,2,0xffffffff),range(16),(0,0x2f3b2,0xffffffff),(0,0x87654321)):
        a=execute(old,0x39744,mapping,state,{},seed,lambda:run_state(state_old,0x39678,0x39b88,first,second,seed))
        b=execute(new,runtime(0x39744),mapped,state,{},seed,lambda:run_state(new,runtime(0x39678),runtime(0x39b88),first,second,seed))
        assert a==b
        expected_state=2 if first==2 else state
        assert ['read_state',expected_state] in b
        assert (['call',0x396a0] in b)==(expected_state==2)
        composed_cases+=1
    return {'composed_boot_state_cases':composed_cases,'cases':cases,'build':evidence,'limits':['Complete dispatcher decoded; initialization helpers and loader call are modeled. Helper state changes test the observed post-call selection read. Hardware effects and composed loader execution remain pending.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-stage1-initialize-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'dispatcher cases passed')
