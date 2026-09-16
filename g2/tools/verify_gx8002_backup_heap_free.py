# SPDX-License-Identifier: MIT
"""Decoded free checks, with modeled diagnostics and merger boundary."""
import itertools,json,re,subprocess
from build_gx8002_backup_heap_free import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=0x200176dc

def put(memory,a,value,size=4):
    for i,b in enumerate((value&((1<<(size*8))-1)).to_bytes(size,'little')):memory[(a+i)&MASK]=b

def execute(code,entry,delta,pointer,memory,seed,mutate):
    memory=memory.copy();r={f'r{i}':(seed+i)&MASK for i in range(32)};r['r0']=pointer;r['r14']=0x20070000;initial=r.copy();pc=entry;condition=False;events=[];saved=None
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r5, r15';saved=(r['r4'],r['r5'],r['r15']);r['r14']-=12
        elif op=='pop':
            assert args=='r4-r5, r15';r['r4'],r['r5'],r['r15']=saved;r['r14']+=12
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return events,memory
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='subi':r[p[0]]=(r[p[1]]-int(p[2],0))&MASK
        elif op in ('addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+(b if op=='addu' else -b))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('br','bt','bf'):
            if op=='br' or (op=='bt' and condition) or (op=='bf' and not condition):nxt=int(p[-1],0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op in ('ld.w','ld.h','st.w','st.h'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&MASK;size=2 if op.endswith('.h') else 4
            if op.startswith('ld'):r[reg]=sum(memory[(a+i)&MASK]<<(8*i) for i in range(size))
            else:
                value=r[reg]&((1<<(8*size))-1);events.append(('write',a,size,value));put(memory,a,value,size)
        elif op=='bsr':
            target=int(args,0)+delta
            if target==0x10009934:
                fmt=r['r0'];assert fmt in (0x10013244,0x10013254,0x10013270)
                events.append(('printf',fmt,*([r['r1'],r['r2'],r['r3']] if fmt==0x10013270 else [])))
                if mutate and fmt==0x10013254:
                    put(memory,pointer-12,0xbeef,2);put(memory,pointer-10,7,2)
                if mutate and fmt==0x10013270:put(memory,STATE,0x2001bb70)
            else:
                assert target==0x100099d4;events.append(('merge',r['r0']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def oracle(pointer,memory,mutate):
    memory=memory.copy();events=[]
    def get(a,size=4):return sum(memory[(a+i)&MASK]<<(8*i) for i in range(size))
    def write(a,v,size=4):
        v&=(1<<(size*8))-1;events.append(('write',a&MASK,size,v));put(memory,a,v,size)
    if not pointer:return events,memory
    base=get(STATE)
    if pointer<base or pointer>=get(STATE+4):return [('printf',0x10013244)],memory
    block=(pointer-12)&MASK
    if not get(block+2,2) or get(block,2)!=0x1ea0:
        events.append(('printf',0x10013254))
        if mutate:put(memory,block,0xbeef,2);put(memory,block+2,7,2)
        events.append(('printf',0x10013270,block,get(block+2,2),get(block,2)))
        if mutate:put(memory,STATE,0x2001bb70)
        base=get(STATE)
    write(block+2,0,2);write(block,0x1ea0,2)
    if block<get(STATE+8):write(STATE+8,block)
    write(STATE+16,block-base+get(STATE+16)-get(block+4));events.append(('merge',block))
    return events,memory

def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x4256c','--stop-address=0x425e4',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-heap-free/free.disassembly.txt').read_text());cases=0;base=0x2001bb80;end=base+256
    for pointer,magic,used,lowest,account,next_offset,seed,mutate in itertools.product((0,base-1,base,base+12,base+28,end-1,end,end+1),(0,0x1ea0,65535),(0,1,65535),(base-16,base+16,end),(0,128,MASK),(0,64,MASK),(0,0xa5a5a5a5),(False,True)):
        memory={};put(memory,STATE,base);put(memory,STATE+4,end);put(memory,STATE+8,lowest);put(memory,STATE+16,account)
        put(memory,pointer-12,magic,2);put(memory,pointer-10,used,2);put(memory,pointer-8,next_offset)
        a=execute(old,0x4256c,0x10000000-0x38940,pointer,memory,seed,mutate);b=execute(new,0x10009c2c,0,pointer,memory,seed,mutate)
        assert a==b==oracle(pointer,memory,mutate),(pointer,magic,used,lowest,account,next_offset,seed,mutate,a,b)
        cases+=1
    report={'build':evidence,'cases':cases,'checks':['Stock/source/oracle ordered writes, diagnostic arguments, merger argument and final memory','Null/range boundaries, invalid headers still freed, wrapped accounting, diagnostic header/state mutation, preserved registers'],'limits':['Merger modeled at call boundary; no complete allocation sequences or concurrent mutation. Ordinary header read order is not compared. Integration pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-heap-free-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(verify()['cases'])
