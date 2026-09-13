# SPDX-License-Identifier: MIT
"""Compare decoded CFFT dispatch; arithmetic helpers are modeled call boundaries."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_cfft import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
DELTA=0x10003000-0x3b940
TARGETS={x+DELTA for x in (0x47d3c,0x47f50,0x47bf4,0x47c98,0x48164)}
def execute(code,entry,delta,length,inverse,reversal,mutate=False):
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=0x1000,r1=0x2000,r2=inverse,r3=reversal,r14=0x9000)
    initial=r.copy();memory={0x1000:length,0x1004:0x100145d4,0x1008:0x100143f4,0x100c:240};events=[];pc=entry;condition=False;saved=None
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r6, r15';saved={k:r[k] for k in ('r4','r5','r6','r15')};r['r14']-=16
        elif op=='pop':
            assert args=='r4-r6, r15' and r['r14']==0x8ff0;r.update(saved);r['r14']+=16
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return events
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op in ('cmpnei','cmphsi'):condition=(r[p[0]]!=int(p[1],0) if op=='cmpnei' else r[p[0]]>=int(p[1],0))
        elif op in ('bf','bt','br','bez','bnez'):
            take=not condition if op=='bf' else condition if op=='bt' else r[p[0]]==0 if op=='bez' else r[p[0]]!=0 if op=='bnez' else True
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','ld.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0);n=4 if op=='ld.w' else 2;value=memory[a];r[reg]=value;events.append(('read',a,n,value))
        elif op=='bsr':
            target=int(args,0)+delta;assert target in TARGETS
            count=4 if target in (0x47d3c+DELTA,0x47f50+DELTA) else 3
            events.append(('call',target,tuple(r[f'r{i}'] for i in range(count))))
            if mutate:
                memory.update({0x1000:16,0x1004:0x11223344,0x1008:0x55667788,0x100c:2})
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xbaad0000+i
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('execution bound')
def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x47b14','--stop-address=0x47bf4',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-cfft/cfft.disassembly.txt').read_text());cases=0
    # Every descriptor length plus boundary flags and helper-induced descriptor changes.
    scenarios=((length,0,0,False) for length in range(65536))
    extra=product((0,1,15,16,17,31,32,33,63,64,65,127,128,129,255,256,257,511,512,513,1023,1024,1025,2047,2048,2049,4095,4096,4097,65535),(0,1,2,255,0xffffffff),(0,1,255,0xffffffff),(False,True))
    from itertools import chain
    for args in chain(scenarios,extra):
        a=execute(old,0x47b14,DELTA,*args);b=execute(new,0x1000f1d4,0,*args);assert a==b,(args,a,b)
        length,inverse,reversal,_=args
        expected=[]
        if length in (16,64,256,1024,4096):expected.append((0x47f50 if inverse==1 else 0x47d3c)+DELTA)
        elif length in (32,128,512,2048):expected.append((0x47c98 if inverse==1 else 0x47bf4)+DELTA)
        if reversal:expected.append(0x48164+DELTA)
        assert [e[1] for e in b if e[0]=='call']==expected
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Exact decoded descriptor reads, helper targets/arguments and preserved registers. Every 16-bit length tested forward without reversal; boundary cases cover inverse/reversal flags and descriptor mutation. Lower arithmetic helpers modeled. Loader and references pending.']}
    (ROOT/'docs/research/gx8002-backup-cfft-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
