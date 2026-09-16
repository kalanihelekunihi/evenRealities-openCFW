# SPDX-License-Identifier: MIT
"""Decoded mask-weighted spectrum smoothing under both MAC models."""
import json,re,random,subprocess
from build_gx8002_imcra_masked_smooth import build,ROOT
from verify_gx8002_memcpy_source import decode
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def signed(v,bits=32):
    v&=(1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,source,arrays,alpha,radius,fused):
    state,inputs,stack=0x21000000,0x21010000,0x30000000
    bins=len(arrays[0])
    r={f'r{i}':0x70000000+i for i in range(32)}
    r.update(r0=state,r1=bins,r2=radius if source else bins-radius,r6=state,r13=bins,r19=radius,r14=stack)
    f={};memory={state+72:alpha,state+116:radius};trace=[];writes=[];condition=False
    for k,field in enumerate((16,31,43,45)):
        base=inputs+k*0x10000;memory[state+field*4]=base
        for i,value in enumerate(arrays[k]):memory[base+i*4]=value
    pc=0x10016090 if source else 0x4e9d0;fp=fused_operation if fused else operation
    for _ in range(bins*(radius*50+150)+200):
        if not source and pc==0x4eb66:return trace,writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.h','ld.hs','flds','fsts'):
            m=re.fullmatch(r'((?:f?r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            if not m:m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='fsts':
                memory[a]=f[reg]
                if a<stack-64:writes.append((a,f[reg]))
            elif op=='flds':
                f[reg]=memory[a]
                if a<stack-64:trace.append((a,4,memory[a]))
            else:
                r[reg]=signed(memory[a],16)&M if op=='ld.hs' else memory[a]
                trace.append((a,4 if op=='ld.w' else 2,memory[a]))
        elif op in ('addi','subi','addu','subu'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op.endswith('i') else r[p[-1]]
            r[p[0]]=(a+b if op.startswith('add') else a-b)&M
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsl':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]<<r[p[-1]])&M
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&M
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='sexth':r[p[0]]=signed(r[p[1]],16)&M
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fsitos':f[p[0]]=fp(op,f[p[1]])
        elif op in ('fmuls','fadds','fsubs','fdivs'):f[p[0]]=fp(op,f[p[1]],f[p[2]])
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op=='fcmpznes':condition=bool(f[p[0]]&0x7fffffff)
        elif op=='fcmplts':condition=fp(op,f[p[0]],f[p[1]])
        elif op=='fmacs':f[p[0]]=fp(op,f[p[1]],f[p[2]],f[p[0]])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('blsz','bnezad','bhz','blz'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            take={'blsz':signed(r[p[0]])<=0,'bhz':signed(r[p[0]])>0,'blz':signed(r[p[0]])<0,'bnezad':r[p[0]]!=0}[op]
            if take:nxt=int(p[1],0)
        elif op in ('fldrs','fstrs'):
            m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(r\d+) << (0|2)\)',args);assert m,args
            reg,base,index,shift=m.groups();a=r[base]+(r[index]<<int(shift))
            if op=='fldrs':f[reg]=memory[a];trace.append((a,4,memory[a]))
            else:memory[a]=f[reg];writes.append((a,f[reg]))
        elif op=='rts':assert source and r['r14']==stack;return trace,writes
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    import struct
    bits=lambda x:int.from_bytes(struct.pack('<f',x),'little')
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4e9d0','--stop-address=0x4eb66',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-masked-smooth/power.disassembly.txt').read_text())
    rng=random.Random(0x4e828);cases=0
    for mask_pattern in (0,1,2):
        for bins in (0,1,2,3,8,257):
            for radius in sorted({0,min(1,bins//2),min(3,bins//2),bins//2}):
                for alpha in (0.0,0.9,1.0):
                    arrays=[[bits(rng.random()*10) for _ in range(bins)] for _ in range(2)]
                    arrays.append([bits(1.0/(radius*2+1))]*(radius*2+1))
                    arrays.append([bits(float(i%2 if mask_pattern==2 else mask_pattern)) for i in range(bins)])
                    for fused in (False,True):
                        a=execute(old,False,arrays,bits(alpha),radius,fused)
                        b=execute(new,True,arrays,bits(alpha),radius,fused)
                        assert a==b,(bins,radius,alpha,fused,a,b)
                        assert len(a[1])==bins
                        if alpha==1.0:
                            assert [value for address,value in a[1]]==arrays[1]
                        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Valid radius 0..bins/2; finite nonnegative arrays, normalized kernel, zero/one/alternating masks and alpha 0/0.9/1.', 'Exact nonstack reads/writes and output bits under separate/fused rational binary32 models.', 'No complete processing, invalid-radius, aliasing or hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-masked-smooth-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
