# SPDX-License-Identifier: MIT
"""Execute stock/source RFFT dispatch; lower transforms are modeled calls."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_rfft import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,delta,length,inverse,reversal,seed,mutation=None):
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=0x1000,r1=0x2000,r2=0x3000,r14=0x9000)
    initial=r.copy();memory={};events=[];pc=entry;condition=False;saved=None
    def store(a,v,n):
        for i in range(n):memory[a+i]=(v>>(8*i))&255
    def load(a,n):return sum(memory[a+i]<<(8*i) for i in range(n))
    for a,v,n in ((0x1000,length,4),(0x1004,inverse,1),(0x1005,reversal,1),(0x1008,1,4),(0x100c,0x100150d8,4),(0x1010,0x100143e4,4)):
        store(a,v,n)
    for i in range(length):store(0x3000+i*2,(seed+i*997)&65535,2)
    for _ in range(10000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r8, r15';saved={k:r[k] for k in ('r4','r5','r6','r7','r8','r15')};r['r14']-=24
        elif op=='pop':
            assert args=='r4-r8, r15' and r['r14']==0x9000-24;r.update(saved);r['r14']+=24
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return events,bytes(memory[0x3000+i] for i in range(length*2))
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('addi','subi','lsri','addu'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a>>b if op=='lsri' else a+b)&0xffffffff
        elif op in ('cmpnei','cmpne','cmphs'):
            a=r[p[0]];b=r[p[1]] if p[1].startswith('r') else int(p[1],0);condition=a>=b if op=='cmphs' else a!=b
        elif op in ('bf','bt','br','bez'):
            take=(not condition if op=='bf' else condition if op=='bt' else r[p[0]]==0 if op=='bez' else True)
            if take:nxt=int(p[-1],0)
        elif op in ('ld.w','ld.b','ld.h','ld.hs','st.w','st.h','stbi.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m
            reg,base,off=m.groups();a=(r[base]+int(off or '0',0))&0xffffffff;n=4 if op.endswith('.w') else 1 if op=='ld.b' else 2
            if op.startswith('ld'):
                value=load(a,n);r[reg]=(value-65536 if op=='ld.hs' and value&32768 else value)&0xffffffff
                events.append(('read',a,n,value))
            else:
                store(a,r[reg],n)
                if a<0x8000:events.append(('write',a,n,r[reg]&((1<<(8*n))-1)))
            if op=='stbi.h':r[base]+=2
        elif op=='bsr':
            target=int(args,0)+delta
            assert target in (0x1000f1d4,0x1000efd4,0x1000f068)
            arguments=tuple(r[f'r{i}'] for i in range(4))
            if target!=0x1000f1d4:arguments+=(load(r['r14'],4),)
            events.append(('call',target,arguments))
            if mutation is not None and target==mutation[0]:
                for address,value,size in mutation[1]:
                    store(address,value,size)
                    events.append(('helper_write',address,size,value&((1<<(8*size))-1)))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xbaad0000+i
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('execution bound')

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x478a4','--stop-address=0x47912',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-backup-rfft/rfft.disassembly.txt').read_text());cases=0
    for length,inverse,reversal,seed in product((0,1,2,7,256,512),(0,1,2,255),(0,1,255),(0,32767,65535)):
        args=(length,inverse,reversal,seed)
        a=execute(old,0x478a4,0x10003000-0x3b940,*args);b=execute(new,0x1000ef64,0,*args)
        assert a==b,(args,a,b)
        expected=b''.join((((seed+i*997)*(2 if inverse==1 else 1))&65535).to_bytes(2,'little') for i in range(length))
        assert b[1]==expected
        calls=[e for e in b[0] if e[0]=='call']
        assert [e[1] for e in calls]==([0x1000f068,0x1000f1d4] if inverse==1 else [0x1000f1d4,0x1000efd4])
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Exact stock/source descriptor and output memory trace, helper arguments and preserved registers; transforms modeled as nonmutating calls. Descriptor mutation and actual transform composition pending.']}
    (ROOT/'docs/research/gx8002-backup-rfft-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
