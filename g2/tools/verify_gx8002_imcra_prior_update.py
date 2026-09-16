# SPDX-License-Identifier: MIT
"""Decoded finite prior-ratio update under both MAC models."""
import json,re,random,subprocess
from build_gx8002_imcra_prior_update import build,ROOT
from verify_gx8002_memcpy_source import decode
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def signed(v,bits=32):
    v&=(1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,source,arrays,alpha,floor,fused):
    state,inputs,stack=0x21000000,0x21010000,0x30000000
    bins=len(arrays[0])
    r={f'r{i}':0x70000000+i for i in range(32)}
    r.update(r0=state if source else inputs,r1=inputs,r2=bins,r6=state,r13=bins,r14=stack)
    f={};memory={state+92:alpha,state+192:floor};trace=[];writes=[];condition=False
    fields=(None,41,42,38,39,17,44)
    for k,field in enumerate(fields):
        base=inputs+k*0x10000
        if field is not None:memory[state+field*4]=base
        for i,value in enumerate(arrays[k]):memory[base+i*4]=value
    pc=0x10015e40 if source else 0x4e77e;fp=fused_operation if fused else operation
    for _ in range(bins*70+100):
        if not source and pc==0x4e828:return trace,writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.h','ld.hs','flds','fsts'):
            m=re.fullmatch(r'((?:f?r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            if not m:m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='fsts':
                memory[a]=f[reg]
                if a<stack-16:writes.append((a,f[reg]))
            elif op=='flds':
                f[reg]=memory[a]
                if a<stack-16:trace.append((a,4,memory[a]))
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
        elif op=='sexth':r[p[0]]=signed(r[p[1]],16)&M
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fsitos':f[p[0]]=fp(op,f[p[1]])
        elif op in ('fmuls','fadds','fsubs','fdivs'):f[p[0]]=fp(op,f[p[1]],f[p[2]])
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op=='fcmplts':condition=fp(op,f[p[0]],f[p[1]])
        elif op=='fmacs':f[p[0]]=fp(op,f[p[1]],f[p[2]],f[p[0]])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        elif op in ('blsz','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            if (signed(r[p[0]])<=0 if op=='blsz' else r[p[0]]!=0):nxt=int(p[1],0)
        elif op in ('fldrs','fstrs'):
            m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(r\d+) << 2\)',args);assert m,args
            reg,base,index=m.groups();a=r[base]+r[index]*4
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
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4e77e','--stop-address=0x4e828',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-prior-update/power.disassembly.txt').read_text())
    rng=random.Random(0x4e77e);cases=0
    for bins in (1,2,3,257):
        for alpha in (0.0,0.92,1.0):
            for pattern in ('zero','random'):
                arrays=[[bits(rng.random()*10 if pattern=='random' else 0) for _ in range(bins)] for _ in range(7)]
                for fused in (False,True):
                    a=execute(old,False,arrays,bits(alpha),0x3e809bcc,fused)
                    b=execute(new,True,arrays,bits(alpha),0x3e809bcc,fused)
                    assert a==b,(bins,alpha,pattern,fused,a,b)
                    assert len(a[1])==bins*4
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Positive-bin noninitial-frame block with finite nonnegative arrays, alpha 0/0.92/1 and observed floor.', 'Exact reads/writes/output bits under separate/fused rational binary32 models; excludes stack accesses.', 'No complete processing, aliasing, NaN or hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-prior-update-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
