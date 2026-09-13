# SPDX-License-Identifier: MIT
"""Decode timer-channel setup, clock query and ordered register writes."""
import json,re,subprocess,random
from build_gx8002_timer_channel_initialize_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,frequency,seed,frequency_hook=None,write_hook=None):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f000
    initial=r.copy();saved=None;trace=[];pc=entry
    for _ in range(32):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='push':
            assert args=='r4-r5, r15' and saved is None
            saved={k:r[k] for k in ('r4','r5','r15')};r['r14']-=12
        elif op=='pop':
            assert args=='r4-r5, r15' and saved is not None and r['r14']==initial['r14']-12
            r.update(saved);r['r14']+=12
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return trace
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
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
            target=int(args,0)+(0x1000dfec if entry==0x177cc else 0)
            assert target==0x10025210 and r['r0']==23 and saved is not None
            trace.append(('frequency',23));value=frequency_hook(23) if frequency_hook else frequency
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(0xbaad0000+i+seed)&MASK
            r['r0']=value
        else:raise ValueError(('timer instruction',op,args))
        pc+=width
    raise ValueError('timer bound')

def expected(frequency):
    return [('write',0xa0400050,1),('write',0xa0400050,0),('write',0xa0400060,1),('frequency',23),('write',0xa0400064,(frequency//1000000-1)&MASK),('write',0xa0400068,0),('write',0xa0400050,2)]

def verify():
    evidence=build();assert evidence['fits'] and sha(IMAGE.read_bytes())==IMAGE_SHA
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(path.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x177cc','--stop-address=0x177fa',str(path)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/timer-channel-initialize-candidate.elf')],text=True))
    rng=random.Random(0x177cc);frequencies=[0,1,999999,1000000,1000001,24576000,0x80000000,MASK,*[rng.getrandbits(32) for _ in range(4096)]]
    for frequency in frequencies:
        for code,entry in ((old,0x177cc),(new,0x100257b8)):
            assert execute(code,entry,frequency,frequency^0x12345678)==expected(frequency)
    return {'candidate':evidence,'decoded_cases':len(frequencies),'source_admitted':False,'limits':['Decoded frequency-call argument, ordered MMIO and callee-saved ABI checked. Frequency provider modeled; integration and physical timer behavior remain pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-timer-channel-initialize-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
