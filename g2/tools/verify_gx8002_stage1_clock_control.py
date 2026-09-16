# SPDX-License-Identifier: MIT
"""Execute source clock helper and predicate together against stock."""
import json,re,subprocess
from itertools import product
from build_gx8002_stage1_clock_control import build
from build_gx8002_backup_cfft import ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,entry,trim,value):
    r={f'r{i}':0x12340000+i for i in range(32)};initial=dict(r);pc=entry;saved=None;trace=[]
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
        elif op=='pop':
            assert args=='r15';r['r15']=saved;r['r14']+=4
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return trace
        elif op=='bsr':r['r15']=nxt;nxt=int(args,0);assert nxt in code
        elif op=='rts':nxt=r['r15']
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&0xffffffff
        elif op in ('and','andi','andni','ori'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=a|b if op=='ori' else a&(~b if op=='andni' else b)
        elif op=='bnez':
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w':
                assert address in (0xa0010030,0xa0010094);r[reg]=trim if address==0xa0010030 else value;trace.append(['read',address,r[reg]])
            else:assert address==0xa0010094;trace.append(['write',address,r[reg]])
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')


def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    tool=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old={}
    for a,b in ((0x39824,0x39830),(0x39c44,0x39c64)):old.update(decode(subprocess.check_output([tool,'-D',f'--start-address={a:#x}',f'--stop-address={b:#x}',str(wrapper)],text=True)))
    new=decode((ROOT/'build/gx8002-stage1-clock-control/state.disassembly.txt').read_text());cases=0
    for trim,high,low in product((0,1,2,3,0xfffffffe,0xffffffff),(0,0x12345600,0xffffff00),range(256)):
        value=high|low;a=execute(old,0x39c44,trim,value);b=execute(new,0x100012f0,trim,value)
        expected=[['read',0xa0010030,trim]]+([] if trim&1 else [['read',0xa0010094,value],['write',0xa0010094,(value&~15)|12]])
        assert a==b==expected;cases+=1
    return {'cases':cases,'build':evidence,'limits':['Both complete source functions execute in one register frame. MMIO values are supplied, with independent ordered read/write oracle; physical clock effects and integration remain pending.']}


if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-stage1-clock-control-execution.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'],'clock-control cases passed')
