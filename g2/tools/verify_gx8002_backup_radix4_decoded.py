# SPDX-License-Identifier: MIT
"""Compare decoded stock DSP with decoded scalar C-SKY radix-4 code."""
import ctypes,json,re,random,subprocess
from build_gx8002_backup_radix4 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_radix4_by2_host import s16
DELTA=0x10003000-0x3b940
MASK=0xffffffff
def signed(v):return v-0x100000000 if v&0x80000000 else v

def execute(code,entry,values,coefficients,modifier):
    length=len(values)//2;mem={}
    def put(a,v,n):
        for i in range(n):mem[a+i]=(v>>(i*8))&255
    def get(a,n):return sum(mem[a+i]<<(8*i) for i in range(n))
    def samples():return tuple(s16(get(0x1000+i*2,2)) for i in range(len(values)))
    for i,v in enumerate(values):put(0x1000+i*2,v,2)
    for i,v in enumerate(coefficients):put(0x8000+i*2,v,2)
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=0x1000,r1=length,r2=0x8000,r3=modifier,r14=0x10000)
    initial=r.copy();pc=entry;condition=False;saved=None
    for _ in range(length*1500+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args in ('r4-r11, r16-r17','r4-r11, r15, r16-r17')
            regs=[f'r{i}' for i in (*range(4,12),16,17)]+(['r15'] if 'r15' in args else []);saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            assert r['r14']==0x10000-4*len(saved);r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            assert all(s16(get(0x8000+i*2,2))==v for i,v in enumerate(coefficients))
            return samples()
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi','addu','subu','lsri','lsli','asri','mult'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            result=a-b if op in ('subi','subu') else a>>b if op=='lsri' else a<<b if op=='lsli' else signed(a)>>b if op=='asri' else a*b if op=='mult' else a+b
            r[p[0]]=result&MASK
        elif op in ('mula.32.l','muls.32.l'):
            product=r[p[1]]*r[p[2]];r[p[0]]=(r[p[0]]+(product if op=='mula.32.l' else -product))&MASK
        elif op in ('max.s32','min.s32'):
            a=signed(r[p[1]]);b=signed(r[p[2]])
            r[p[0]]=(max(a,b) if op=='max.s32' else min(a,b))&MASK
        elif op=='andni':r[p[0]]=r[p[1]]&(~int(p[2],0)&MASK)
        elif op=='nor':r[p[0]]=~(r[p[0] if len(p)==2 else p[1]]|r[p[-1]])&MASK
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='add.64':
            def pair(reg):return r[reg]|(r['r'+str((int(reg[1:])+1)%32)]<<32)
            v=(pair(p[1])+pair(p[2]))&0xffffffffffffffff
            r[p[0]]=v&MASK;r['r'+str((int(p[0][1:])+1)%32)]=v>>32
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('bhz','bnez'):
            if (signed(r[p[0]])>0 if op=='bhz' else r[p[0]]!=0):nxt=int(p[1],0)
        elif op=='bsr':
            r['r15']=nxt;nxt=int(p[0],0)
            assert nxt in code
        elif op=='rts':nxt=r['r15']
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='bloop':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
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
                assert all(a+i in mem or 0xff00<=a+i<0x10000 for i in range(n));put(a,r[reg],n)
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
        elif op in ('padd.s16.s','psub.s16.s','psubh.s16','pasx.s16.s','psax.s16.s','pasxh.s16','psaxh.s16'):
            a,b=r[p[1]],r[p[2]];lo,hi,bl,bh=s16(a),s16(a>>16),s16(b),s16(b>>16)
            sat=lambda v:max(-32768,min(32767,v))
            if op=='padd.s16.s':x,y=sat(lo+bl),sat(hi+bh)
            elif op=='psub.s16.s':x,y=sat(lo-bl),sat(hi-bh)
            elif op=='psubh.s16':x,y=(lo-bl)>>1,(hi-bh)>>1
            else:
                x,y=(lo-bh,hi+bl) if op.startswith('pasx') else (lo+bh,hi-bl)
                x,y=(sat(x),sat(y)) if op.endswith('.s') else (x>>1,y>>1)
            r[p[0]]=(x&65535)|((y&65535)<<16)
        elif op in ('mulca.s16.s','mulcsx.s16','mulcs.s16','mulcax.s16.s'):
            a,b=r[p[1]],r[p[2]];lo,hi,bl,bh=s16(a),s16(a>>16),s16(b),s16(b>>16)
            if op=='mulca.s16.s':v=min(2147483647,lo*bl+hi*bh)
            elif op=='mulcax.s16.s':v=min(2147483647,lo*bh+hi*bl)
            elif op=='mulcs.s16':v=lo*bl-hi*bh
            else:v=lo*bh-hi*bl
            r[p[0]]=v&MASK
        elif op=='pkghh':r[p[0]]=(r[p[1]]>>16)|(r[p[2]]&0xffff0000)
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('execution bound')

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert elf.contents(next(s for s in elf.sections if s['name']=='.data'))==stock
    from generate_gx8002_backup_math_tables import coefficients as generate
    raw=generate(complex_fft=True);table=raw[0] if isinstance(raw,tuple) else raw
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-backup-radix4';rng=random.Random(0x48164);cases=0
    for inverse,start,end in ((0,0x47d3c,0x47f50),(1,0x47f50,0x48164)):
        old=decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True))
        name='inverse' if inverse else 'forward';new=decode((out/(name+'.disassembly.txt')).read_text());e=Elf32((out/(name+'.elf')).read_bytes(),name)
        symbol='open_cfw_gx8002_backup_radix4'+('_inverse' if inverse else '')
        entry=next(s['value'] for s in e.symbols() if s['name']==symbol)
        for length in (16,64,256):
          for trial in range(12):
            edge=(-32768,-32767,-1,0,1,32766,32767)
            values=[edge[(i+trial)%7] if trial<7 else rng.randrange(-32768,32768) for i in range(2*length)]
            for random_table in (False,True):
                coefficients=[rng.randrange(-32768,32768) for _ in table] if random_table else table
                a=execute(old,start,values,coefficients,256//length)
                b=execute(new,entry,values,coefficients,256//length)
                assert a==b,(inverse,length,trial,random_table,[(i,x,y) for i,(x,y) in enumerate(zip(a,b)) if x!=y][:8])
                cases+=1
    report={'build':evidence,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Both stock packed DSP and actual scalar C-SKY instructions executed, including compiled multiply helper. Complete output buffers, coefficients and callee-saved registers checked.','Finite forward/inverse lengths 16/64/256 with generated/random coefficients and extreme/random samples. Disjoint ordinary RAM only; access ordering and widths differ.','Candidate entry resolved from ELF symbols; original-address placement is invalid due to size. No loader or hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-radix4-decoded-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['decoded_cases'])
