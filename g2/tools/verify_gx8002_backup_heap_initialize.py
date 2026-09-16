# SPDX-License-Identifier: MIT
"""Decoded heap setup against independent alignment and block-write oracle."""
import json,re,subprocess,itertools
from build_gx8002_backup_heap_initialize import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=0x200176dc


def execute(code,entry,delta,begin,end,seed):
    r={f'r{i}':(seed+i)&MASK for i in range(32)};r['r0']=begin;r['r1']=end;r['r14']=0x20070000;initial=r.copy();pc=entry;saved=None;condition=False;events=[];memory={}
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':assert args=='r4, r15';saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            assert args=='r4, r15';r['r4'],r['r15']=saved;r['r14']+=8
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return events,memory
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','andni','bclri'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]={'addi':lambda:a+b,'subi':lambda:a-b,'andni':lambda:a&~b,'bclri':lambda:a&~(1<<b)}[op]()&MASK
        elif op in ('addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+(b if op=='addu' else -b))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('br','bt','bf'):
            if op=='br' or (op=='bt' and condition) or (op=='bf' and not condition):nxt=int(p[-1],0)
        elif op in ('st.w','st.h','ld.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=sum(memory[(a+i)&MASK]<<(8*i) for i in range(4))
            else:
                size=2 if op=='st.h' else 4;value=r[reg]&((1<<(size*8))-1);events.append(('write',a,size,value))
                for i,b in enumerate(value.to_bytes(size,'little')):memory[(a+i)&MASK]=b
        elif op=='bsr':
            assert int(args,0)+delta==0x10009934;events.append(('printf',r['r0'],r['r1'],r['r2']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('Execution bound')


def oracle(begin,end):
    lo=((begin+3)&MASK)&~3;hi=end&~3
    if hi<=24 or hi-24<lo:return [('printf',0x100131d8,begin,end)]
    usable=hi-24-lo;next_offset=usable+12;last=(lo+next_offset)&MASK
    return [('write',STATE+12,4,usable),('write',STATE,4,lo),('printf',0x100131ac,lo,usable),('write',lo,2,0x1ea0),('write',(lo+8)&MASK,4,0),('write',(lo+2)&MASK,2,0),('write',(lo+4)&MASK,4,next_offset),('write',last,2,0x1ea0),('write',STATE+4,4,last),('write',(last+2)&MASK,2,1),('write',(last+4)&MASK,4,next_offset),('write',(last+8)&MASK,4,next_offset),('write',STATE+8,4,lo)]


def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x42384','--stop-address=0x423f8',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-heap-initialize/heap.disassembly.txt').read_text())
    values=list(range(33))+[0x2001bb80,0x2002cb80,0xfffffffc,0xfffffffd,0xfffffffe,0xffffffff];cases=0
    for begin,end,seed in itertools.product(values,values,(0,0xa5a5a5a5)):
        a=execute(old,0x42384,0x10000000-0x38940,begin,end,seed);b=execute(new,0x10009a44,0,begin,end,seed)
        assert a==b and a[0]==oracle(begin,end)
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Synthetic addresses test unsigned arithmetic, not physical memory validity. Printf modeled without state mutation. Exact ordered stores, final touched bytes and ABI checked; concurrent access and allocator sequences pending.']}
    (ROOT/'docs/research/gx8002-backup-heap-initialize-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':print(verify()['cases'])
