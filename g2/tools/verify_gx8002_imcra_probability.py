# SPDX-License-Identifier: MIT
"""Decoded probability estimation with explicit finite conversion/reciprocal models."""
import json,re,random,subprocess
from build_gx8002_imcra_probability import build,ROOT
from verify_gx8002_memcpy_source import decode
from gx8002_binary32_rational import operation,fused_operation
M=0xffffffff

def signed(v,bits=32):
    v&=(1<<bits)-1
    return v-(1<<bits) if v&(1<<(bits-1)) else v

def execute(code,source,arrays,parameters,bins,fused,mode):
    state,inputs,stack=0x21000000,0x21010000,0x30000000
    r={f'r{i}':0x70000000+i for i in range(32)}
    r.update(r0=state,r1=bins,r6=state,r13=bins,r14=stack)
    f={};memory={state+76:parameters[0],state+80:parameters[1],state+88:parameters[2],state+84:parameters[1],state+188:mode};trace=[];writes=[];condition=False
    for k,field in enumerate((33,31,32,46,16,30,44,39)):
        base=inputs+k*0x10000;memory[state+field*4]=base
        for i,value in enumerate(arrays[k]):memory[base+i*4]=value
    pc=0x10016228 if source else 0x4eb66;fp=fused_operation if fused else operation
    for _ in range(max(0,bins)*90+200):
        if not source and pc==0x4ec8c:return trace,writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.h','ld.hs','flds','fsts','st.w'):
            m=re.fullmatch(r'((?:f?r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            if not m:m=re.fullmatch(r'(fr\d+),\s*\((r\d+),\s*(0x[0-9a-f]+)\)',args)
            assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op in ('fsts','st.w'):
                value=f[reg] if op=='fsts' else r[reg]
                memory[a]=value
                if a<stack-16:writes.append((a,value))
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
        elif op=='lsri':r[p[0]]=r[p[1]]>>int(p[2],0)
        elif op=='sexth':r[p[0]]=signed(r[p[1]],16)&M
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fsitos':f[p[0]]=fp(op,f[p[1]])
        elif op in ('fmuls','fadds','fsubs','fdivs'):f[p[0]]=fp(op,f[p[1]],f[p[2]])
        elif op=='fmovs':f[p[0]]=f[p[1]]
        elif op in ('fcmplts','fcmphss'):condition=fp(op,f[p[0]],f[p[1]])
        elif op in ('fmacs','fnmacs'):f[p[0]]=fp(op,f[p[1]],f[p[2]],f[p[0]])
        elif op=='fstoui.rz':
            import struct
            value=struct.unpack('<f',f[p[1]].to_bytes(4,'little'))[0]
            assert 0<=value<4294967296
            f[p[0]]=int(value)
        elif op=='frecips':f[p[0]]=fp(op,f[p[1]])
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
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
        elif op=='str.w':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(r\d+) << 0\)',args);assert m,args
            reg,base,index=m.groups();a=r[base]+r[index];memory[a]=r[reg];writes.append((a,r[reg]))
        elif op=='rts':assert source and r['r14']==stack;return trace,writes
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    import struct
    bits=lambda x:int.from_bytes(struct.pack('<f',x),'little')
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x4eb66','--stop-address=0x4f0fe',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-imcra-probability/power.disassembly.txt').read_text())
    cases=0
    for weight in (0.0,0.25,8.0):
        for bins in (1,2,17,257):
            for mode in (0,2):
                for fused in (False,True):
                    arrays=[[bits(v) for _ in range(bins)] for v in (1,2,1.25,0,0,0,weight,0.5)]
                    for kind in range(6):
                        arrays[4]=[bits((0.5,1.66,2.0,4.98,8.0,2.0)[kind]) for _ in range(bins)]
                        arrays[5]=[bits(4 if kind==5 else 0.5) for _ in range(bins)]
                        a=execute(old,False,arrays,list(map(bits,(1.66,3,1.67))),bins,fused,mode)
                        b=execute(new,True,arrays,list(map(bits,(1.66,3,1.67))),bins,fused,mode)
                        assert a==b,(bins,mode,fused,kind,a,b)
                        assert len(a[1])==bins*2
                        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Positive bins, modes 0/2, finite threshold cases and in-range float-to-uint approximation.', 'Exact nonstack reads/writes and output bits under separate/fused rational models; reciprocal modeled as correctly rounded division, not hardware-qualified.', 'No full processing, NaN, wide conversion or aliasing qualification.']}
    (ROOT/'docs/research/gx8002-imcra-probability-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
