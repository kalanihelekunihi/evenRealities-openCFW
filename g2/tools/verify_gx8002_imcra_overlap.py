# SPDX-License-Identifier: MIT
"""Decoded overlap-output/tail block; excludes inverse FFT and caller ABI."""
import json,re,random,subprocess
from build_gx8002_imcra_synthesize import build,ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def signed(v,bits=32):
    v&=(1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,source,arrays,hop,framecounter):
    state=0x21000000;output=0x21100000;frame=len(arrays[0]);memory={state+20:hop,state+12:frame,state+32:framecounter};trace=[]
    for k,field in enumerate((14,12,11,13)):
        base=0x21010000+k*0x10000;memory[state+field*4]=base
        for i,v in enumerate(arrays[k]):memory[base+2*i]=v&0xffff
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r4=state if source else output,r5=output,r6=state)
    pc=0x100164a6 if source else 0x4edd4;stop=0x10016564 if source else 0x4ee50;condition=False
    for _ in range(frame*50+200):
        if pc==stop:return trace,memory
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.h','st.w','st.h','ldbi.h','stbi.h','ldr.h','str.h'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(r\d+) << 1\)',args)
            if m:reg,base,index=m.groups();address=r[base]+r[index]*2
            else:
                m=re.fullmatch(r'(r\d+),\s*\((r\d+)(?:,\s*(0x[0-9a-f]+))?\)',args);assert m,args
                reg,base,offset=m.groups();address=r[base]+int(offset or '0',0)
            size=4 if op.endswith('.w') else 2
            if op.startswith('ld'):r[reg]=memory[address];trace.append(('read',address,size,r[reg]))
            else:memory[address]=r[reg]&((1<<(8*size))-1);trace.append(('write',address,size,memory[address]))
            if 'bi.' in op:r[base]+=size
        elif op in ('addu','subu','addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op.endswith('i') else r[p[-1]]
            r[p[0]]=(a+b if op.startswith('add') else a-b)&M
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='nor':r[p[0]]=~(r[p[-1]]|r[p[-2]])&M
        elif op in ('lsli','lsri','asri'):
            a=r[p[1]];b=int(p[2],0);r[p[0]]=((a<<b) if op=='lsli' else signed(a)>>b if op=='asri' else a>>b)&M
        elif op=='mulsh':r[p[0]]=(signed(r[p[1] if len(p)==3 else p[0]],16)*signed(r[p[-1]],16))&M
        elif op=='sext':r[p[0]]=signed(r[p[1]]>>int(p[3],0),int(p[2],0)-int(p[3],0)+1)&M
        elif op=='sexth':r[p[0]]=signed(r[p[1]],16)&M
        elif op=='max.s32':r[p[0]]=max(signed(r[p[1]]),signed(r[p[2]]))&M
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op in ('bt','br'):
            if op=='br' or condition:nxt=int(args,0)
        elif op in ('blsz','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            if (signed(r[p[0]])<=0 if op=='blsz' else r[p[0]]!=0):nxt=int(p[1],0)
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4edd4','--stop-address=0x4ee50',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-synthesize/prepare.disassembly.txt').read_text())
    rng=random.Random(0x4edd4);cases=0
    for frame in (0,1,2,3,256,512):
        for hop in sorted({0,frame//2,frame}):
            for pattern in ('random','extrema','zero'):
                arrays=[[rng.randrange(-32768,32768) if pattern=='random' else (-32768,32767,-1,0,16384)[(i+k)%5] if pattern=='extrema' else 0 for i in range(frame)] for k in range(4)]
                for counter in (0,0xffffffff):
                    a=execute(old,False,arrays,hop,counter);b=execute(new,True,arrays,hop,counter)
                    assert a==b,(frame,hop,pattern)
                    expected=[]
                    for i in range(hop):
                        windowed=(arrays[0][i]*arrays[1][i])>>15
                        total=signed(arrays[2][i]+windowed,16)
                        value=max(-32767,signed((total*arrays[3][i])>>14,16))
                        expected.append(value&0xffff)
                    assert [a[1][0x21100000+i*2] for i in range(hop)]==expected
                    expected_tail=[((arrays[0][i]*arrays[1][i])>>15)&0xffff for i in range(hop,frame)]
                    assert [a[1][0x21030000+i*2] for i in range(frame-hop)]==expected_tail
                    assert a[1][0x21000020]==(counter+1)&M
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded overlap-output, tail and counter only; exact ordered memory effects plus independent output arithmetic oracle.', 'Valid nonnegative dimensions and disjoint arrays; excludes helper execution, synthesis entry, stack/ABI and hardware.']}
    (ROOT/'docs/research/gx8002-imcra-overlap-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
