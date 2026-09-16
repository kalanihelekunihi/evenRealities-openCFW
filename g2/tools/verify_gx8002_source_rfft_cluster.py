# SPDX-License-Identifier: MIT
"""Execute the linked source RFFT component with real compiled helper calls."""
import ctypes,json,re,random,subprocess
from build_gx8002_backup_radix4 import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_backup_radix4_by2_host import s16
DELTA=0x10003000-0x3b940
MASK=0xffffffff
def signed(v):return v-0x100000000 if v&0x80000000 else v

def execute(code,entry,values,rodata,descriptor,output_count):
    length=len(values)//2;mem={}
    def put(a,v,n):
        for i in range(n):mem[a+i]=(v>>(i*8))&255
    def get(a,n):return sum(mem[a+i]<<(8*i) for i in range(n))
    def samples():return tuple(s16(get(0x1000+i*2,2)) for i in range(len(values)))
    for i,v in enumerate(values):put(0x1000+i*2,v,2)
    for i in range(output_count):put(0x4000+i*2,0x5a5a,2)
    mem.update(rodata)
    readonly=dict(rodata)
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=descriptor,r1=0x1000,r2=0x4000,r3=0,r14=0x10000)
    initial=r.copy();pc=entry;condition=False;frames=[]
    for _ in range(length*1500+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            regs=[]
            for part in p:
                if '-' in part:
                    first,last=part.split('-');regs.extend(f'r{i}' for i in range(int(first[1:]),int(last[1:])+1))
                else:regs.append(part)
            saved={k:r[k] for k in regs};r['r14']-=4*len(regs);frames.append((saved,r['r14']))
        elif op=='pop':
            saved,sp=frames.pop();assert r['r14']==sp;r.update(saved);r['r14']+=4*len(saved)
            if not frames:
                assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
                assert all(mem[a]==v for a,v in readonly.items())
                return samples(),tuple(s16(get(0x4000+i*2,2)) for i in range(output_count))
            if 'r15' in saved:nxt=r['r15']
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='sexth':r[p[0]]=s16(r[p[1]])&MASK
        elif op=='abs':r[p[0]]=abs(signed(r[p[1]]))&MASK
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('xor','and'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]];r[p[0]]=a^b if op=='xor' else a&b
        elif op=='bhsz':
            if signed(r[p[0]])>=0:nxt=int(p[1],0)
        elif op=='or':r[p[0]]=r[p[0] if len(p)==2 else p[1]]|r[p[-1]]
        elif op in ('mul.s32','mula.s32'):
            nextreg='r'+str((int(p[0][1:])+1)%32)
            v=signed(r[p[1]])*signed(r[p[2]])
            if op=='mula.s32':v+=r[p[0]]|(r[nextreg]<<32)
            v&=0xffffffffffffffff;r[p[0]]=v&MASK;r[nextreg]=v>>32
        elif op=='str.h':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args);assert m,args
            reg,base,index,shift=m.groups();a=r[base]+(r[index]<<int(shift))
            assert 0x4000<=a and a+2<=0x4000+output_count*2;put(a,r[reg],2)
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
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='bloop':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('cmpne','cmplt'):
            condition=(r[p[0]]!=r[p[1]]) if op=='cmpne' else signed(r[p[0]])<signed(r[p[1]])
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(p[0],0)
        elif op in ('ld.b','ld.w','ld.hs','ld.h','ldbi.w','ldbi.h','st.w','st.h','stbi.w','stbi.h','pldbi.d'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args);assert m,args
            reg,base,off=m.groups();a=r[base]+int(off or '0',0);n=1 if op=='ld.b' else 8 if op=='pldbi.d' else 4 if op.endswith('.w') else 2
            if op=='pldbi.d':
                v=get(a,8);r[reg]=v&MASK;r['r'+str(int(reg[1:])+1)]=v>>32
            elif op.startswith('ld'):
                v=get(a,n);r[reg]=(s16(v) if op=='ld.hs' else v)&MASK
            else:
                assert all((0x1000<=a+i<0x1000+len(values)*2) or 0x4000<=a+i<0x4000+output_count*2 or 0xfe00<=a+i<0x10000 for i in range(n));put(a,r[reg],n)
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

def verify(shared_radix4=False,shared_by2=False,lto=False,generated_reverse=False,placed=False,include_fill=False,combined_lto=False,tail_layout=False,startup=False):
    from build_gx8002_source_rfft_cluster import build as cluster
    from verify_gx8002_backup_radix4_stock_host import execute as radix
    from verify_gx8002_backup_split_stock_host import execute as split
    from generate_gx8002_backup_math_tables import coefficients as generate
    evidence=cluster(shared_radix4=shared_radix4,shared_by2=shared_by2,generated_reverse=generated_reverse);out=ROOT/('build/gx8002-source-rfft-generated-reverse-cluster' if generated_reverse else 'build/gx8002-source-rfft-double-shared-cluster' if shared_by2 else 'build/gx8002-source-rfft-shared-cluster' if shared_radix4 else 'build/gx8002-source-rfft-cluster')
    if lto:
        assert shared_radix4 and shared_by2 and not generated_reverse
        from probe_gx8002_fft_lto import probe
        lto_report=probe();assert lto_report['exit_code']==0 and not lto_report['undefined_symbols']
        out=ROOT/'build/gx8002-fft-lto-probe'
        evidence={'source_build':evidence,'lto':lto_report}
    if placed:
        assert generated_reverse and shared_radix4 and shared_by2 and not lto
        from build_gx8002_placed_rfft_cluster import build as place
        evidence=place(include_fill=include_fill);out=ROOT/('build/gx8002-placed-rfft-fill-cluster' if include_fill else 'build/gx8002-placed-rfft-cluster')
    artifact='cluster'
    if combined_lto:
        assert shared_radix4 and shared_by2 and generated_reverse and not placed and not lto
        from probe_gx8002_q15_cluster_lto import probe
        evidence=probe(include_fft=True);out=ROOT/'build/gx8002-fft-q15-cluster-lto-probe';artifact='cluster-1'
    if tail_layout:
        assert generated_reverse and shared_radix4 and shared_by2 and not (placed or lto or combined_lto)
        from build_gx8002_fft_q15_tail_layout import build as tail
        evidence=tail();out=ROOT/'build/gx8002-fft-q15-tail-layout';artifact='component'
    if startup:
        assert placed and not include_fill
        out=ROOT/'build/gx8002-backup-startup-cluster';artifact='cluster'
        evidence['startup_cluster_sha256']=sha((out/'cluster.elf').read_bytes())
    elf=Elf32((out/(artifact+'.elf')).read_bytes(),'RFFT');code=decode((out/(artifact+'.disassembly.txt')).read_text())
    memory={s['address']+i:v for s in elf.sections if s['flags']&2 and not s['flags']&4 for i,v in enumerate(elf.contents(s))};symbols={s['name']:s['value'] for s in elf.symbols() if s['name']}
    if lto or combined_lto or tail_layout:evidence['entry']=symbols['open_cfw_gx8002_backup_rfft']
    stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');complex_coeff=generate(complex_fft=True)[0];real_coeff=generate()[0];rng=random.Random(512);cases=0
    def reverse(values):return tuple(values[2*int(f'{i:08b}'[::-1],2)+j] for i in range(256) for j in (0,1))
    for inverse in (0,1):
        rstart,rend=(0x47f50,0x48164) if inverse else (0x47d3c,0x47f50);sstart,send=(0x479a8,0x47a00) if inverse else (0x47914,0x479a8)
        rc=decode(subprocess.check_output([pre,'-D',f'--start-address={rstart:#x}',f'--stop-address={rend:#x}',str(wrapper)],text=True));sc=decode(subprocess.check_output([pre,'-D',f'--start-address={sstart:#x}',f'--stop-address={send:#x}',str(wrapper)],text=True))
        for trial in range(12):
            values=[(-32768 if i%2 else 32767) if trial==0 else rng.randrange(-32768,32768) for i in range(514 if inverse else 512)]
            if inverse:
                intermediate=split(sc,sstart,values,real_coeff,256,1,True)
                transformed=reverse(radix(rc,rstart,intermediate,complex_coeff,1))
                expected=tuple(s16(v*2) for v in transformed);expected_input=tuple(values)
            else:
                expected_input=reverse(radix(rc,rstart,values,complex_coeff,1))
                expected=split(sc,sstart,expected_input,real_coeff,256,1,False)
            descriptor=symbols['source_rfft_inverse' if inverse else 'source_rfft_forward']
            actual_input,actual_output=execute(code,evidence['entry'],values,memory,descriptor,len(expected))
            assert actual_input==expected_input and actual_output==expected,(inverse,trial)
            cases+=1
    report={'build':evidence,'linked_rfft_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Full linked 512-point forward/inverse source RFFT execution, real internal calls and linked descriptors/tables. Both input and output buffers match composed decoded stock arithmetic.','Extreme and random samples; fixed shipped descriptor flags. Finite instruction model, not hardware/timing proof.','Analysis-address component; valid firmware layout and external-entry qualification pending.']}
    if placed:
        report['limits'][-1]='Placed in original FFT ranges with fixed RFFT entry and descriptors; loader, external reference closure and hardware qualification pending.'
    (ROOT/('docs/research/gx8002-startup-rfft-verification.json' if startup else 'docs/research/gx8002-fft-q15-tail-rfft-verification.json' if tail_layout else 'docs/research/gx8002-fft-q15-lto-rfft-verification.json' if combined_lto else 'docs/research/gx8002-placed-rfft-fill-verification.json' if placed and include_fill else 'docs/research/gx8002-placed-rfft-verification.json' if placed else 'docs/research/gx8002-source-rfft-generated-reverse-verification.json' if generated_reverse else 'docs/research/gx8002-source-rfft-lto-verification.json' if lto else 'docs/research/gx8002-source-rfft-double-shared-cluster-verification.json' if shared_by2 else 'docs/research/gx8002-source-rfft-shared-cluster-verification.json' if shared_radix4 else 'docs/research/gx8002-source-rfft-cluster-verification.json')).write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['linked_rfft_cases'])
