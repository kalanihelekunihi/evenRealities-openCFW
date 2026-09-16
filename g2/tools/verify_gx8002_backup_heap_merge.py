# SPDX-License-Identifier: MIT
"""Compare decoded coalescing over synthetic linked-block configurations."""
import itertools,json,re,subprocess
from build_gx8002_backup_heap_merge import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
STATE=0x200176dc

def execute(code,entry,pointer,memory,seed):
    memory=memory.copy();r={f'r{i}':(seed+i)&MASK for i in range(32)};r['r0']=pointer;initial=r.copy();pc=entry;condition=False;events=[]
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
            return events,memory
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op in ('addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+(b if op=='addu' else -b))&MASK
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('br','bt','bf'):
            if op=='br' or (op=='bt' and condition) or (op=='bf' and not condition):nxt=int(p[-1],0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('ld.w','ld.h','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&MASK;size=2 if op=='ld.h' else 4
            if op.startswith('ld'):
                r[reg]=sum(memory[(a+i)&MASK]<<(8*i) for i in range(size));events.append(('read',a,size,r[reg]))
            else:
                events.append(('write',a,size,r[reg]))
                for i,b in enumerate(r[reg].to_bytes(4,'little')):memory[(a+i)&MASK]=b
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();assert sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x42314','--stop-address=0x42384',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-heap-merge/merge.disassembly.txt').read_text());cases=0
    for base,used0,used2,lowest,previous,next_offset,seed in itertools.product((0x2001bb80,0xffffffc0),(0,1,65535),(0,1,65535),range(4),(0,16),(16,32,48),(0,0xa5a5a5a5)):
        memory={}
        def put(a,value,size=4):
            for i,b in enumerate(value.to_bytes(size,'little')):memory[(a+i)&MASK]=b
        for i in range(4):
            a=(base+16*i)&MASK;put(a,0x1ea0,2);put(a+2,[used0,0,used2,1][i],2);put(a+4,min(i+1,3)*16);put(a+8,max(i-1,0)*16)
        pointer=(base+16)&MASK;put(pointer+4,next_offset);put(pointer+8,previous)
        put(STATE,base);put(STATE+4,(base+48)&MASK);put(STATE+8,(base+16*lowest)&MASK)
        a=execute(old,0x42314,pointer,memory,seed);b=execute(new,0x100099d4,pointer,memory,seed)
        assert a==b,(base,used0,used2,lowest,previous,next_offset,seed,a,b)
        cases+=1
    report={'build':evidence,'cases':cases,'checks':['Exact ordered reads and writes, final memory, and callee-saved registers','Forward, backward, both and neither merge; self links, sentinel and lowest-free selection; wrapping addresses'],'limits':['Synthetic block configurations; no concurrent mutation, allocator sequence or hardware execution. Integration pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-heap-merge-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report

if __name__=='__main__':print(verify()['cases'])
