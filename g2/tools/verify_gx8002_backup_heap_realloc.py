# SPDX-License-Identifier: MIT
"""Decoded malloc comparison with modeled printf."""
import itertools,json,re,subprocess
from build_gx8002_backup_heap_realloc import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=0x200176dc

def put(memory,a,value,size=4):
    for i,b in enumerate((value&((1<<(size*8))-1)).to_bytes(size,'little')):memory[(a+i)&MASK]=b

def execute(code,entry,delta,pointer,requested,memory,seed,replacement):
    memory=memory.copy();r={f'r{i}':(seed+i)&MASK for i in range(32)};r['r0']=pointer;r['r1']=requested;r['r14']=0x20070000;initial=r.copy();pc=entry;condition=False;events=[];saved=None
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r7, r15';saved=tuple(r[f'r{i}'] for i in (4,5,6,7,15));r['r14']-=20
        elif op=='pop':
            assert args=='r4-r7, r15';r['r4'],r['r5'],r['r6'],r['r7'],r['r15']=saved;r['r14']+=20
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],events,memory
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','andni','bclri'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]={'addi':lambda:a+b,'subi':lambda:a-b,'andni':lambda:a&~b,'bclri':lambda:a&~(1<<b)}[op]()&MASK
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='min.u32':r[p[0]]=min(r[p[1]],r[p[2]])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+(b if op=='addu' else -b))&MASK
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('br','bt','bf'):
            if op=='br' or (op=='bt' and condition) or (op=='bf' and not condition):nxt=int(p[-1],0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('ld.w','ld.h','st.w','st.h'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&MASK;size=2 if op.endswith('.h') else 4
            if op.startswith('ld'):r[reg]=sum(memory[(a+i)&MASK]<<(8*i) for i in range(size))
            else:
                value=r[reg]&((1<<(8*size))-1);events.append(('write',a,size,value));put(memory,a,value,size)
        elif op=='bsr':
            target=int(args,0)+delta
            result=0
            if target==0x10009934:
                assert r['r0']==0x100132a0;events.append(('printf',r['r0']))
            elif target==0x10009ab8:events.append(('malloc',r['r0']));result=replacement
            elif target==0x10009c2c:events.append(('free',r['r0']))
            elif target==0x100099d4:events.append(('merge',r['r0']))
            elif target==0x10011344:events.append(('memcpy',r['r0'],r['r1'],r['r2']));result=r['r0']
            else:raise AssertionError(hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x425e4','--stop-address=0x426bc',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-heap-realloc/realloc.disassembly.txt').read_text());cases=0;base=0x2001bb80
    for pointer,request,next_offset,used,lowest,replacement,seed in itertools.product((0,base-1,base,base+12,base+28,base+256),list(range(0,81))+[243,244,245,256,MASK-3,MASK-2,MASK],(64,128,256),(0,128,MASK),(base,base+128),(0,0x2001c000),(0,0xa5a5a5a5)):
        memory={base+i:0xa5 for i in range(-16,300)}
        for off,value in enumerate((base,base+256,base+lowest-base,244,used,256)):put(memory,STATE+4*off,value)
        put(memory,pointer-8,next_offset)
        a=execute(old,0x425e4,0x10000000-0x38940,pointer,request,memory,seed,replacement);b=execute(new,0x10009ca4,0,pointer,request,memory,seed,replacement)
        assert a==b,(pointer,request,next_offset,used,lowest,replacement,seed,a,b)
        cases+=1
    report={'build':evidence,'cases':cases,'checks':['Decoded return, ordered writes, call arguments, final memory and preserved registers','Null/range/size boundaries, strict shrink threshold, allocation failure and wrapped accounting'],'limits':['Malloc/free/merge/memcpy/printf modeled at call boundaries; no nested allocator execution or independent oracle. Candidate fits; integration pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-heap-realloc-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(verify()['cases'])
