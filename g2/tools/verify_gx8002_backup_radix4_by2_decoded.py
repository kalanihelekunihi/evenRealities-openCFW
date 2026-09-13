# SPDX-License-Identifier: MIT
"""Execute stock packed DSP and compiled scalar butterfly candidates."""
import json,re,random,subprocess
from build_gx8002_backup_radix4_by2 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_radix4_by2_host import s16,reference
DELTA=0x10003000-0x3b940
MASK=0xffffffff
def signed(v):return v-0x100000000 if v&0x80000000 else v

def execute(code,entry,delta,values,coefficients,inverse,mutate=False,helper=None):
    length=len(values)//2;mem={};calls=[]
    def put(a,v,n):
        for i in range(n):mem[a+i]=(v>>(i*8))&255
    def get(a,n):return sum(mem[a+i]<<(8*i) for i in range(n))
    def samples():return tuple(s16(get(0x1000+i*2,2)) for i in range(len(values)))
    for i,v in enumerate(values):put(0x1000+i*2,v,2)
    for i,v in enumerate(coefficients):put(0x8000+i*2,v,2)
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=0x1000,r1=length,r2=0x8000,r14=0x10000)
    initial=r.copy();pc=entry;condition=False;saved=None
    for _ in range(length*100+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            match=re.fullmatch(r'r4-r(\d+), r15',args);assert match,args
            regs=[f'r{i}' for i in range(4,int(match[1])+1)]+['r15'];saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            assert r['r14']==0x10000-4*len(saved);r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            assert all(s16(get(0x8000+i*2,2))==v for i,v in enumerate(coefficients))
            return samples(),calls
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi','addu','subu','lsri','lsli','asri','mult'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            result=a-b if op in ('subi','subu') else a>>b if op=='lsri' else a<<b if op=='lsli' else signed(a)>>b if op=='asri' else a*b if op=='mult' else a+b
            r[p[0]]=result&MASK
        elif op in ('mula.32.l','muls.32.l'):
            product=r[p[1]]*r[p[2]];r[p[0]]=(r[p[0]]+(product if op=='mula.32.l' else -product))&MASK
        elif op in ('cmpne','cmplt'):
            condition=(r[p[0]]!=r[p[1]]) if op=='cmpne' else signed(r[p[0]])<signed(r[p[1]])
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(p[0],0)
        elif op in ('ld.w','ld.hs','ld.h','ldbi.w','ldbi.h','st.w','st.h','stbi.w','stbi.h','pldbi.d'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m,args
            reg,base,off=m.groups();a=r[base]+int(off or '0',0);n=8 if op=='pldbi.d' else 4 if op.endswith('.w') else 2
            if op=='pldbi.d':
                v=get(a,8);r[reg]=v&MASK;r['r'+str(int(reg[1:])+1)]=v>>32
            elif op.startswith('ld'):
                v=get(a,n);r[reg]=(s16(v) if op=='ld.hs' else v)&MASK
            else:
                assert all(a+i in mem for i in range(n));put(a,r[reg],n)
            if 'bi.' in op:r[base]=(r[base]+n)&MASK
        elif op in ('pasri.s16','plsli.16','psub.16','paddh.s16','pmul.s16','pmulx.s16'):
            a=r[p[1]];lo=s16(a);hi=s16(a>>16)
            if op in ('pasri.s16','plsli.16'):
                n=int(p[2],0);x,y=(lo>>n,hi>>n) if op=='pasri.s16' else (lo<<n,hi<<n)
            else:
                b=r[p[2]];bl,bh=s16(b),s16(b>>16)
                if op=='psub.16':x,y=lo-bl,hi-bh
                elif op=='paddh.s16':x,y=(lo+bl)>>1,(hi+bh)>>1
                else:
                    x,y=(lo*bl,hi*bh) if op=='pmul.s16' else (lo*bh,hi*bl)
                    r[p[0]]=x&MASK;r['r'+str((int(p[0][1:])+1)%32)]=y&MASK;pc=nxt;continue
            r[p[0]]=(x&65535)|((y&65535)<<16)
        elif op=='bsr':
            target=int(p[0],0)+delta;assert target==(0x47f50 if inverse else 0x47d3c)+DELTA
            argv=tuple(r[f'r{i}'] for i in range(4));calls.append((target,argv,samples()))
            assert argv==(0x1000+(length*2 if len(calls)==2 else 0),length//2,0x8000,2)
            if helper is not None:
                block=[s16(get(argv[0]+2*i,2)) for i in range(argv[1]*2)]
                transformed=helper(block,coefficients,argv[3])
                assert len(transformed)==len(block)
                for i,value in enumerate(transformed):put(argv[0]+2*i,value,2)
            if mutate:
                for i in range(length):
                    a=argv[0]+2*i;put(a,get(a,2)^((i*997+0x8001)&65535),2)
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xbaad0000+i
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('execution bound')

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');rng=random.Random(0x47c98);cases=0
    for inverse,start,end in ((0,0x47bf4,0x47c98),(1,0x47c98,0x47d3c)):
        old=decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True))
        name='inverse' if inverse else 'forward';new=decode((ROOT/f'build/gx8002-backup-radix4-by2/{name}.disassembly.txt').read_text())
        for length in (0,2,4,16,32,128,512,2048):
          for trial in range(12):
            edge=(-32768,-32767,-1,0,1,32766,32767)
            values=[edge[(i+trial)%7] if trial<7 else rng.randrange(-32768,32768) for i in range(2*length)]
            coefficients=[edge[(i+trial*3)%7] if trial<7 else rng.randrange(-32768,32768) for i in range(length)]
            for mutate in (False,True):
                a=execute(old,start,DELTA,values,coefficients,inverse,mutate);b=execute(new,start+DELTA,0,values,coefficients,inverse,mutate)
                assert a==b,(inverse,length,trial,mutate)
                if not mutate:assert list(a[0])==reference(values,coefficients,inverse)
                cases+=1
    report={'build':evidence,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Exact sample buffers at both lower-helper call boundaries and return; exact call arguments and preserved registers.','Packed stock and scalar compiled instruction models; memory access widths/order differ, so disjoint ordinary RAM buffers required.','Lower radix-4 helpers modeled as no-ops or deterministic buffer mutations. Full lower arithmetic, timing and hardware not qualified; candidates exceed original envelopes.']}
    (ROOT/'docs/research/gx8002-backup-radix4-by2-decoded-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['decoded_cases'])
