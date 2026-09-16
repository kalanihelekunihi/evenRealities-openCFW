# SPDX-License-Identifier: MIT
"""Decoded first-frame smoothing and initialization copies."""
import json,re,random,subprocess
from build_gx8002_imcra_first_frame import build,ROOT
from verify_gx8002_memcpy_source import decode
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def signed(v,bits=32):
    v&=(1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,source,arrays,radius,histories,fused,mutate=False):
    state,inputs,stack=0x21000000,0x21010000,0x30000000
    bins=len(arrays[0])
    r={f'r{i}':0x70000000+i for i in range(32)}
    r.update(r0=state,r1=bins,r2=bins*4,r6=state,r13=bins,r14=stack)
    f={};memory={state+116:radius,state+28:bins,state+108:histories};trace=[];writes=[];condition=False
    for k,field in enumerate((16,30,43,31,32,33,35,37,41,40,34,36)):
        base=inputs+k*0x10000;memory[state+field*4]=base
        data=arrays[k] if k<3 else [0]*(bins*max(1,histories)+16)
        for i,value in enumerate(data):memory[base+i*4]=value
    pc=0x10016648 if source else 0x4ef88;fp=fused_operation if fused else operation
    calls=0
    for _ in range(bins*(radius*50+150)+histories*50+300):
        if not source and pc==0x4f0d4:return trace,writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='ldbi.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)\)',args);assert m,args
            reg,base=m.groups();address=r[base];r[reg]=memory[address];trace.append((address,4,memory[address]));r[base]+=4
        elif op in ('ld.w','ld.h','ld.hs','flds','fsts','st.w','ldbi.w'):
            m=re.fullmatch(r'((?:f?r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            if not m:m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op in ('fsts','st.w'):
                memory[a]=f[reg] if op=='fsts' else r[reg]
                if a<stack-64:writes.append((a,memory[a]))
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
        elif op=='push':pass
        elif op=='pop':assert source;return trace,writes
        elif op=='mult':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]*r[p[-1]])&M
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&M
        elif op=='bsr':
            assert int(args,0)==(0x10011344 if source else 0x49c84)
            destination,origin,count=r['r0'],r['r1'],r['r2'];assert count%4==0
            trace.append(('copy',destination,origin,count));calls+=1
            for offset in range(0,count,4):memory[destination+offset]=memory[origin+offset];writes.append((destination+offset,memory[origin+offset]))
            if mutate and calls==1:memory[state+28]=max(0,bins-1)
            if mutate and calls==9:memory[state+108]=min(histories,1)
            for i in (0,1,2,3,12,13,*range(18,32)):r[f'r{i}']=0x60000000+i
            r['r0']=destination
        elif op=='rts':assert source and r['r14']==stack;return trace,writes
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    import struct
    bits=lambda x:int.from_bytes(struct.pack('<f',x),'little')
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4ef88','--stop-address=0x4f0d4',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-first-frame/prepare.disassembly.txt').read_text())
    rng=random.Random(0x4ef88);cases=0
    for bins in (0,1,2,3,17,257):
        for radius in sorted({0,min(1,bins//2),min(3,bins//2)}):
            for histories in (0,1,4):
                arrays=[[bits(rng.random()*10) for _ in range(bins)], [0]*bins, [bits(1/(radius*2+1))]*(radius*2+1)]
                for fused in (False,True):
                    for mutate in (False,True):
                        a=execute(old,False,arrays,radius,histories,fused,mutate)
                        b=execute(new,True,arrays,radius,histories,fused,mutate)
                        assert a==b,(bins,radius,histories,fused,mutate,a,b)
                        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded first-frame path with modeled copying, clobbered caller registers and count/history mutations.', 'Exact ordered state/data reads, copy calls and writes under both rational binary32 MAC models; copy internals not traced.', 'Valid dimensions, finite nonnegative powers and normalized kernels. No ABI, physical helpers, aliasing or full processing qualification.']}
    (ROOT/'docs/research/gx8002-imcra-first-frame-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
