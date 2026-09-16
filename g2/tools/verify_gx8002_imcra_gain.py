# SPDX-License-Identifier: MIT
"""Decoded synthesis gain application and integer truncation."""
import json,re,random,subprocess
from build_gx8002_imcra_synthesize import build,ROOT
from verify_gx8002_memcpy_source import decode
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def signed(v,bits=32):
    v&=(1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,source,values,gains,bins):
    state,inputs,outputs,stack=0x21000000,0x21010000,0x21020000,0x30000000
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=state,r1=outputs,r2=bins&M,r3=0,r5=0,r6=state,r13=bins&M,r14=stack)
    f={};memory={state+60:inputs,state+68:outputs};trace=[];writes=[];condition=False
    for i,v in enumerate(values):memory[inputs+i*2]=v&0xffff
    for i,v in enumerate(gains):memory[outputs+i*4]=v
    pc=0x10016404 if source else 0x4ed44;fp=operation
    for _ in range(max(bins,0)*40+50):
        if pc==(0x10016470 if source else 0x4ed9c):return trace,writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.h','ld.hs','flds','fsts','st.h'):
            m=re.fullmatch(r'((?:f?r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            if not m:m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='fsts':
                memory[a]=f[reg]
                if a<stack-16:writes.append((a,f[reg]))
            elif op=='st.h':
                memory[a]=r[reg]&0xffff;writes.append((a,memory[a]));trace.append(('write',a,2,memory[a]))
            elif op=='flds':
                f[reg]=memory[a];trace.append(('read',a,4,memory[a]))
            else:
                value=memory[a] if op=='ld.w' else memory[a]&0xffff
                r[reg]=signed(value,16)&M if op=='ld.hs' else value
                if a<stack-64:trace.append(('read',a,4 if op=='ld.w' else 2,value))
        elif op in ('addi','subi','addu','subu'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op.endswith('i') else r[p[-1]]
            r[p[0]]=(a+b if op.startswith('add') else a-b)&M
        elif op=='push':pass # Prologue save is outside this block's ABI claim.
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsl':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]<<r[p[-1]])&M
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&M
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='sexth':r[p[0]]=signed(r[p[1]],16)&M
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op in ('fsitos','fstosi.rz'):f[p[0]]=fp(op,f[p[1]])
        elif op=='fmuls':f[p[0]]=fp(op,f[p[1]],f[p[2]])
        elif op=='fmacs':f[p[0]]=fp(op,f[p[1]],f[p[2]],f[p[0]])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op in ('blsz','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            if (signed(r[p[0]])<=0 if op=='blsz' else r[p[0]]!=0):nxt=int(p[1],0)
        elif op=='rts':assert source and r['r14']==stack;return trace,writes
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    import struct
    bits=lambda x:int.from_bytes(struct.pack('<f',x),'little')
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4ed44','--stop-address=0x4ed9c',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-synthesize/prepare.disassembly.txt').read_text())
    rng=random.Random(0x4ed44);cases=0
    for bins in (-1,0,1,2,3,257):
        for gain in (0.0,0.25,0.5,0.9,1.0,2.0,-0.5):
            for pattern in ('zero','extrema','random'):
                values=[rng.randrange(-32768,32768) if pattern=='random' else (-32768,32767,-1,1)[i%4] if pattern=='extrema' else 0 for i in range(max(0,bins)*2)]
                gains=[bits(gain)]*max(0,bins)
                a=execute(old,False,values,gains,bins);b=execute(new,True,values,gains,bins)
                assert a==b,(bins,gain,pattern,a,b)
                expected=[]
                for v in values:
                    rounded=struct.unpack('<f',struct.pack('<f',v*struct.unpack('<f',struct.pack('<f',gain))[0]))[0]
                    expected.append(int(rounded)&0xffff)
                assert [v for address,v in a[1]]==expected
                cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded gain block only, finite Q15 samples and gains with int32-range products.', 'Exact ordered nonstack sample/gain accesses and writes; independent binary32 multiply/truncation oracle.', 'Excludes synthesis helper execution, stack/ABI and hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-gain-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
