# SPDX-License-Identifier: MIT
"""Decoded finite power-spectrum block execution under both MAC models."""
import json,re,random,subprocess
from build_gx8002_imcra_power_spectrum import build,ROOT
from verify_gx8002_memcpy_source import decode
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def signed(v,bits=32):
    v&=(1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,source,values,shift,bins,fused):
    state,inputs,outputs,stack=0x21000000,0x21010000,0x21020000,0x30000000
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=state,r1=shift&M,r5=shift&M,r6=state,r14=stack)
    f={};memory={state+28:bins&M,state+60:inputs,state+64:outputs};trace=[];writes=[];condition=False
    for i,v in enumerate(values):memory[inputs+i*2]=v&0xffff
    pc=0x10015ddc if source else 0x4e71a;fp=fused_operation if fused else operation
    for _ in range(max(bins,0)*40+50):
        if not source and pc in (0x4e776,0x4ef7c):return trace,writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.h','ld.hs','flds','fsts'):
            m=re.fullmatch(r'((?:f?r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            if not m:m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='fsts':
                memory[a]=f[reg]
                if a<stack-16:writes.append((a,f[reg]))
            elif op=='flds':f[reg]=memory[a]
            else:
                r[reg]=signed(memory[a],16)&M if op=='ld.hs' else memory[a]
                trace.append((a,4 if op=='ld.w' else 2,memory[a]))
        elif op in ('addi','subi','addu','subu'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op.endswith('i') else r[p[-1]]
            r[p[0]]=(a+b if op.startswith('add') else a-b)&M
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsl':r[p[0]]=(r[p[0] if len(p)==2 else p[1]]<<r[p[-1]])&M
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&M
        elif op=='sexth':r[p[0]]=signed(r[p[1]],16)&M
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fsitos':f[p[0]]=fp(op,f[p[1]])
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
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4e71a','--stop-address=0x4e776',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-power-spectrum/power.disassembly.txt').read_text())
    rng=random.Random(0x4e71a);cases=0
    for bins in (-1,0,1,2,3,257):
        for shift in range(-9,2):
            for pattern in ('zero','extrema','random'):
                values=[rng.randrange(-32768,32768) if pattern=='random' else ((-32768,32767,-1,0)[i%4] if pattern=='extrema' else 0) for i in range(max(0,bins)*2)]
                for fused in (False,True):
                    a=execute(old,False,values,shift,bins,fused);b=execute(new,True,values,shift,bins,fused)
                    assert a==b,(bins,shift,pattern,fused)
                    assert len(a[1])==max(0,bins)
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Finite Q15 inputs and shifts -9..1; exact nonstack read/write traces and output bits under separate/fused rational binary32 MAC models.', 'Standalone block only; no complete processing, hardware FPU, timing or aliasing qualification.']}
    (ROOT/'docs/research/gx8002-imcra-power-spectrum-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
