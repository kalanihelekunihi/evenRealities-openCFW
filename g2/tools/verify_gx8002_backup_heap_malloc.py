# SPDX-License-Identifier: MIT
"""Decoded malloc comparison with modeled printf."""
import itertools,json,re,subprocess
from build_gx8002_backup_heap_malloc import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=0x200176dc

def put(memory,a,value,size=4):
    for i,b in enumerate((value&((1<<(size*8))-1)).to_bytes(size,'little')):memory[(a+i)&MASK]=b

def execute(code,entry,delta,pointer,memory,seed,mutate):
    memory=memory.copy();r={f'r{i}':(seed+i)&MASK for i in range(32)};r['r0']=pointer;r['r14']=0x20070000;initial=r.copy();pc=entry;condition=False;events=[];saved=None
    for _ in range(1000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4, r15';saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            assert args=='r4, r15';r['r4'],r['r15']=saved;r['r14']+=8
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return r['r0'],events,memory
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','andni','bclri'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]={'addi':lambda:a+b,'subi':lambda:a-b,'andni':lambda:a&~b,'bclri':lambda:a&~(1<<b)}[op]()&MASK
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='max.u32':r[p[0]]=max(r[p[1]],r[p[2]])
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
            assert target==0x10009934
            fmt=r['r0'];assert fmt in (0x10013214,0x10013238)
            events.append(('printf',fmt,*([r['r1'],r['r2']] if fmt==0x10013214 else [])))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x423f8','--stop-address=0x4254c',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-heap-malloc/malloc.disassembly.txt').read_text());cases=0;base=0x2001bb80
    requests=list(range(0,81))+[127,128,129,244,245,255,256,257,MASK-3,MASK-2,MASK-1,MASK]
    for request,flags,lowest,account,maximum,seed in itertools.product(requests,itertools.product((0,1),repeat=3),(0,64,128,256),(0,64,MASK),(0,128,MASK),(0,0xa5a5a5a5)):
        memory={((base+i)&MASK):0xa5 for i in range(280)}
        offsets=[0,64,128,256]
        for i,offset in enumerate(offsets):
            put(memory,base+offset,0x1ea0,2);put(memory,base+offset+2,flags[i] if i<3 else 1,2)
            put(memory,base+offset+4,offsets[min(i+1,3)]);put(memory,base+offset+8,offsets[max(i-1,0)])
        for off,value in enumerate((base,base+256,base+lowest,244,account,maximum)):put(memory,STATE+off*4,value)
        a=execute(old,0x423f8,0x10000000-0x38940,request,memory,seed,False);b=execute(new,0x10009ab8,0,request,memory,seed,False)
        assert a==b,(request,flags,lowest,account,maximum,seed,a,b)
        cases+=1
    report={'build':evidence,'cases':cases,'checks':['Decoded stock/source return, ordered writes, printf arguments, final memory and preserved registers','Split/no-split boundaries, used/free block combinations, lowest-free positions, unsigned request and statistics wrap'],'limits':['Fixed synthetic heap layout; printf modeled without mutation. No independent allocation oracle, full sequences or concurrent access. Integration pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-heap-malloc-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(verify()['cases'])
