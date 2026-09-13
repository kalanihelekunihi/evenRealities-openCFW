# SPDX-License-Identifier: MIT
"""Execute stock radix-4 instructions for native C comparison; target C pending."""
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
    for _ in range(length*200+100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            assert args=='r4-r11, r16-r17'
            regs=[f'r{i}' for i in (*range(4,12),16,17)];saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
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
    manifest=json.loads((ROOT/'docs/research/gx8002-csky-dsp-upstream-evidence.json').read_text())
    for row in manifest['files']:assert sha((ROOT/'build/upstream-xuantie-qemu-csky'/row['file']).read_bytes())==row['sha256']
    from generate_gx8002_backup_math_tables import coefficients as generate
    raw=generate(complex_fft=True);table=raw[0] if isinstance(raw,tuple) else raw
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-backup-radix4';rng=random.Random(0x47d3c);cases=0
    for inverse,start,end in ((0,0x47d3c,0x47f50),(1,0x47f50,0x48164)):
        old=decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True))
        path=out/('stock-host-'+str(inverse)+'.dylib')
        subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror','-dynamiclib','-DINVERSE='+str(inverse),str(ROOT/'components/shared/gx8002/runtime_gx8002_backup_radix4.c'),'-o',str(path)],check=True)
        lib=ctypes.CDLL(str(path));fn=getattr(lib,'open_cfw_gx8002_backup_radix4'+('_inverse' if inverse else ''))
        fn.argtypes=[ctypes.POINTER(ctypes.c_int16),ctypes.c_uint,ctypes.POINTER(ctypes.c_int16),ctypes.c_uint]
        for length in (16,64,256):
          for trial in range(20):
            edge=(-32768,-32767,-1,0,1,32766,32767)
            values=[edge[(i+trial)%7] if trial<7 else rng.randrange(-32768,32768) for i in range(2*length)]
            for random_table in (False,True):
                coefficients=[rng.randrange(-32768,32768) for _ in table] if random_table else table
                expected=execute(old,start,values,coefficients,256//length)
                data=(ctypes.c_int16*len(values))(*values);twiddle=(ctypes.c_int16*len(coefficients))(*coefficients)
                fn(data,length,twiddle,256//length)
                assert tuple(data)==expected,(inverse,length,trial,random_table,[(i,a,b) for i,(a,b) in enumerate(zip(data,expected)) if a!=b][:8])
                assert list(twiddle)==list(coefficients);cases+=1
    report={'build':evidence,'stock_native_cases':cases,'vendor_evidence':manifest,'source_admitted':False,'hardware_qualified':False,'limits':['Decoded stock instruction model versus native macOS C, complete output buffers; compiled C-SKY candidate not executed.','Forward/inverse lengths 16/64/256, generated and random coefficient tables, extrema and random inputs. Vendor semantics model is not hardware proof.','Code still exceeds original layout; no firmware integration.']}
    (ROOT/'docs/research/gx8002-backup-radix4-stock-host-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['stock_native_cases'])
