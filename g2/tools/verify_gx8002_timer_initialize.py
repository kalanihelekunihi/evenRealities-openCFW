# SPDX-License-Identifier: MIT
"""Decode timer-channel setup, clock query and ordered register writes."""
import json,re,subprocess,random
from build_gx8002_timer_initialize_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,frequency,seed,helper_hook=None,write_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f000
    initial=r.copy();saved=None;trace=[];pc=entry
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            assert args=='r4-r7, r15' and saved is None
            saved={k:r[k] for k in ('r4','r5','r6','r7','r15')};r['r14']-=20
        elif op=='pop':
            assert args=='r4-r7, r15' and saved is not None and r['r14']==initial['r14']-20
            r.update(saved);r['r14']+=20
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return trace
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='nor':r[p[0]]=~(r[p[0]]|r[p[1]])&MASK
        elif op=='lsl':r[p[0]]=(r[p[0]]<<r[p[1]])&MASK
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='rotli':
            value=r[p[1]];shift=int(p[2],0);r[p[0]]=((value<<shift)|(value>>(32-shift)))&MASK
        elif op=='divu':
            assert r[p[2]]!=0;r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();trace.append(('write',(r[base]+int(off,0))&MASK,r[reg]))
            if write_hook is not None:write_hook((r[base]+int(off,0))&MASK,r[reg])
        elif op=='bsr':
            target=int(args,0)+(0x1000dfec if entry==0x177fc else 0)
            assert saved is not None
            counts={0x10025080:2,0x10025210:1,0x102099cc:3,0x1002553c:3,0x100257b8:0}
            assert target in counts
            arguments=tuple(r[f'r{i}'] for i in range(counts[target]))
            trace.append(('call',target,*arguments))
            value=frequency if target==0x10025210 else seed
            if helper_hook is not None:value=helper_hook(target,arguments,value)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xbaad0000+i+seed)&MASK
            r['r0']=value
        else:raise ValueError(('timer instruction',op,args))
        pc+=width
    raise ValueError('timer bound')

def expected(frequency):
    return [('call',0x10025080,23,1),('write',0xa0400010,1),('write',0xa0400010,0),('write',0xa0400020,3),('call',0x10025210,23),('write',0xa0400024,(frequency//1000000-1)&MASK),('write',0xa0400028,0xfffffc18),('write',0xa0400010,2),('call',0x102099cc,0x20026d84,0,360),('call',0x1002553c,14,0x100258c4,0),('call',0x100257b8),('write',0xa0400090,1),('write',0xa0400090,0),('write',0xa04000a0,1),('write',0xa04000a4,0),('write',0xa04000a8,0),('write',0xa0400090,2)]


def verify():
    evidence=build();assert evidence['fits'] and sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(path.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x177fc','--stop-address=0x17870',str(path)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-initialize-candidate.elf')],text=True))
    rng=random.Random(0x177fc);frequencies=[0,1,999999,1000000,1000001,24576000,0x80000000,MASK,*[rng.getrandbits(32) for _ in range(4096)]]
    for frequency in frequencies:
        for code,entry in ((old,0x177fc),(new,0x100257e8)):
            assert execute(code,entry,frequency,frequency^0x12345678)==expected(frequency)
    return {'candidate':evidence,'decoded_cases':len(frequencies),'source_admitted':False,'limits':['Decoded outer timer ordered MMIO, helper arguments and callee-saved ABI checked. All helper effects modeled; slot state clearing, dependency composition and hardware remain pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
