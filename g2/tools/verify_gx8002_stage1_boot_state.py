# SPDX-License-Identifier: MIT
"""Compare boot-state selector with changing descriptor reads."""
import json,re,subprocess
from itertools import product
from build_gx8002_stage1_boot_state import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,helper,first,second,seed):
    r={f'r{i}':(seed+i*0x10203)&0xffffffff for i in range(32)};initial=dict(r);saved=None;pc=entry;condition=False;trace=[];reads=0
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r15';saved=r['r15'];r['r14']=(r['r14']-4)&0xffffffff
        elif op=='pop':
            assert args=='r15';r['r15']=saved;r['r14']=(r['r14']+4)&0xffffffff
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace
        elif op in ('lrw','movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op in ('and','andi','andni'):
            left=r[p[0] if len(p)==2 else p[1]];right=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=left&(~right if op=='andni' else right)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='bsr':
            assert int(args,0)==helper;trace.append(['hardware_helper'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xdead0000^i)&0xffffffff
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w':
                assert address==0xa0010068 and reads<2;r[reg]=first if reads==0 else second;reads+=1
                trace.append(['read',address,r[reg]])
            else:
                assert address in (0x20001720,0x20001724);trace.append(['write',address,r[reg]])
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('selector bound')


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([tool,'-D','--start-address=0x39678','--stop-address=0x396a0',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-stage1-boot-state/state.disassembly.txt').read_text());cases=0
    for low,high,second,seed in product(range(16),(0,0xfffffff0,0x12345670),(0,2,255,256,0x2f3b2,0xffffffff),(0,0x87654321)):
        first=high|low
        a=execute(old,0x39678,0x39b88,first,second,seed);b=execute(new,0x10000d24,0x10001234,first,second,seed)
        expected=[['hardware_helper'],['read',0xa0010068,first]]
        if low==2:expected += [['write',0x20001720,2],['read',0xa0010068,second],['write',0x20001724,second&0xffffff00]]
        assert a==b==expected;cases+=1
    return {'cases':cases,'build':evidence,'limits':['Complete selector instructions and ordered reads/writes compared with independent oracle and ABI checks. Initial hardware helper is modeled as returning and clobbering caller registers. No dispatcher composition, physical hardware or integration qualification.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-stage1-boot-state-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'boot-state selector cases passed')
