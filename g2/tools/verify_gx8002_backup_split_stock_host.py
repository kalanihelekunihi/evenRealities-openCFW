# SPDX-License-Identifier: MIT
"""Decoded stock split arithmetic versus native C; target execution pending."""
import ctypes,json,random,re,subprocess
from build_gx8002_backup_split import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
def s16(x):return (x&65535)-65536 if x&32768 else x&65535
def s32(x):return (x&MASK)-0x100000000 if x&0x80000000 else x&MASK
def sat(x):return max(-2147483648,min(2147483647,x))
def execute(code,entry,values,coefficients,half,modifier,inverse):
    memory={}
    def put(a,v,n):
        for i in range(n):memory[a+i]=(v>>(8*i))&255
    def get(a,n):return sum(memory[a+i]<<(8*i) for i in range(n))
    for i,v in enumerate(values):put(0x1000+2*i,v,2)
    for i,v in enumerate(coefficients):put(0x4000+2*i,v,2)
    count=half*2 if inverse else (half+1)*2
    for i in range(count):put(0x8000+2*i,0x5a5a,2)
    put(0x10000,modifier,4)
    r={f'r{i}':0x76540000+i for i in range(32)};r.update(r0=0x1000,r1=half,r2=0x4000,r3=0x8000,r14=0x10000);initial=r.copy();pc=entry;saved=None
    for _ in range(half*40+100):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            assert args in ('r4','r4-r7');regs=['r4'] if args=='r4' else ['r4','r5','r6','r7'];saved={k:r[k] for k in regs};r['r14']-=4*len(regs)
        elif op=='pop':
            assert r['r14']==0x10000-4*len(saved);r.update(saved);r['r14']+=4*len(saved)
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            assert all(s16(get(0x1000+i*2,2))==v for i,v in enumerate(values))
            assert all(s16(get(0x4000+i*2,2))==v for i,v in enumerate(coefficients))
            return tuple(s16(get(0x8000+2*i,2)) for i in range(count))
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi','addu','lsli'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a<<b if op=='lsli' else a+b)&MASK
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='bloop':
            r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('ld.w','ld.hs','ldbi.w','ldbir.w','st.h','stbi.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)(?:, (r\d+))?',args);assert m,args
            reg,base,off,increment=m.groups();a=r[base]+int(off or '0',0);n=2 if op in ('ld.hs','st.h') else 4
            if op.startswith('ld'):
                v=get(a,n);r[reg]=(s16(v) if op=='ld.hs' else v)&MASK
            else:
                assert 0x8000<=a and a+n<=0x8000+count*2;put(a,r[reg],n)
            if op in ('ldbi.w','stbi.w','ldbir.w'):r[base]+=r[increment] if increment else n
        elif op in ('psub.16','pabs.s16.s','pneg.s16.s','pkg','pkghh','addh.s32','subh.s32'):
            a=r[p[1]]
            if op=='pkg':r[p[0]]=((a>>int(p[2],0))&65535)|(((r[p[3]]>>int(p[4],0))&65535)<<16)
            elif op=='pkghh':r[p[0]]=(a>>16)|(r[p[2]]&0xffff0000)
            elif op in ('addh.s32','subh.s32'):r[p[0]]=((s32(a)+(s32(r[p[2]]) if op=='addh.s32' else -s32(r[p[2]])))>>1)&MASK
            else:
                lo,hi=s16(a),s16(a>>16)
                if op=='psub.16':b=r[p[2]];x,y=lo-s16(b),hi-s16(b>>16)
                elif op=='pabs.s16.s':x,y=min(abs(lo),32767),min(abs(hi),32767)
                else:x,y=min(-lo,32767),min(-hi,32767)
                r[p[0]]=(x&65535)|((y&65535)<<16)
        elif op.startswith('mul'):
            a,b=r[p[1]],r[p[2]];lo,hi,bl,bh=s16(a),s16(a>>16),s16(b),s16(b>>16)
            if op=='mulcs.s16':v=lo*bl-hi*bh
            elif op=='mulcsx.s16':v=lo*bh-hi*bl
            elif op=='mulcax.s16.s':v=sat(lo*bh+hi*bl)
            elif op=='mulaca.s16.s':v=sat(s32(r[p[0]])+s32(lo*bl+hi*bh))
            elif op=='mulacax.s16.s':v=sat(s32(r[p[0]])+s32(lo*bh+hi*bl))
            elif op=='mulacsx.s16.s':v=sat(s32(r[p[0]])+s32(lo*bh-hi*bl))
            else:raise ValueError(op)
            r[p[0]]=v&MASK
        else:raise ValueError((hex(pc),op,args))
        pc=nxt
    raise ValueError('bound')

def verify():
    evidence=build();stock=IMAGE.read_bytes();assert sha(stock)==IMAGE_SHA
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock');assert e.contents(next(s for s in e.sections if s['name']=='.data'))==stock
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-backup-split';rng=random.Random(0x47914);cases=0
    from generate_gx8002_backup_math_tables import coefficients as generate
    raw=generate();table=raw[0] if isinstance(raw,tuple) else raw
    for inverse,start,end in ((0,0x47914,0x479a8),(1,0x479a8,0x47a00)):
        old=decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(wrapper)],text=True))
        path=out/('host-'+str(inverse)+'.dylib');subprocess.run(['clang','-O2','-Wall','-Wextra','-Werror','-dynamiclib','-DINVERSE='+str(inverse),str(ROOT/'components/shared/gx8002/runtime_gx8002_backup_split.c'),'-o',str(path)],check=True)
        lib=ctypes.CDLL(str(path));name='inverse' if inverse else 'forward';fn=getattr(lib,'open_cfw_gx8002_backup_split_'+name);ptr=ctypes.POINTER(ctypes.c_int16);fn.argtypes=[ptr,ctypes.c_uint,ptr,ptr,ctypes.c_uint]
        for half,modifier in ((1,1),(2,1),(16,1),(64,2),(256,1)):
          for trial in range(12):
            values=[(-32768 if i%2 else 32767) if trial==0 else rng.randrange(-32768,32768) for i in range((half+1)*2)]
            for random_table in (False,True):
                coefficients=[rng.randrange(-32768,32768) for _ in table] if random_table else table
                expected=execute(old,start,values,coefficients,half,modifier,inverse)
                data=(ctypes.c_int16*len(values))(*values);coef=(ctypes.c_int16*len(coefficients))(*coefficients);output=(ctypes.c_int16*len(expected))(*([0x5a5a]*len(expected)))
                fn(data,half,coef,output,modifier)
                assert tuple(output)==expected,(inverse,half,trial,random_table,[(i,a,b) for i,(a,b) in enumerate(zip(output,expected)) if a!=b][:8])
                cases+=1
    report={'build':evidence,'stock_native_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Native macOS C versus decoded stock splitting including packed negation and coefficient complement, whole output buffers. Compiled C-SKY execution pending.','Positive half lengths 1/2/16/64/256, stride 1/2, generated/random coefficients and extreme/random samples; disjoint RAM buffers only.','Original placement exceeded; no loader or hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-split-stock-host-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['stock_native_cases'])
