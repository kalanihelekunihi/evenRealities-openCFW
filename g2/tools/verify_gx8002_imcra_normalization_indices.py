# SPDX-License-Identifier: MIT
"""Execute normalization integer addressing/loop control; FPU body checked separately."""
import json,re,subprocess
from build_gx8002_backup_imcra_state import ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def run(code,source,length):
    r={f'r{i}':0 for i in range(32)};r.update(r9=length&M,r14=0x8000)
    if source:r.update(r4=0x20010000,r6=0x20011000,r7=0x20012000)
    else:r.update(r7=0x20011000,r8=0x20012000)
    pc=0x1000e5d8 if source else 0x46f48;end=0x1000e5fc if source else 0x46fb2;condition=False;reads=[];writes=[]
    def signed(x):return x if x<0x80000000 else x-0x100000000
    for _ in range(40000):
        if pc==end:return reads,writes
        op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addu','addi','lsri','lsli','asri'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=r[p[-1]] if op=='addu' else int(p[-1],0)
            r[p[0]]=((a+b) if op in ('addu','addi') else a>>b if op=='lsri' else a<<b if op=='lsli' else signed(a)>>b)&M
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op=='blsz':
            if signed(r[p[0]])<=0:nxt=int(p[1],0)
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='ld.w':assert source and args=='r2, (r4, 0xc)';r['r2']=length&M
        elif op in ('ld.hs','ldbi.hs'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)(?:,\s*0x0)?\)',args);assert m,args
            dest,base=m.groups();reads.append(r[base]);r[dest]=0
            if op=='ldbi.hs':r[base]+=2
        elif op=='ldr.h':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(r\d+) << 0\)',args);assert m,args
            dest,base,index=m.groups();reads.append(r[base]+r[index]);r[dest]=0
        elif op=='str.h':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(r\d+) << 1\)',args);assert m,args
            _,base,index=m.groups();writes.append(r[base]+r[index]*2)
        elif op=='stbi.h':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)\)',args);assert m,args
            _,base=m.groups();writes.append(r[base]);r[base]+=2
        elif op=='ld.h':r[p[0]]=0 # stock stack transfer of converted value
        elif op=='sexth':pass
        elif op in ('fmtvrl','fsitos','fmuls','fmacs','frecips','fstosi.rz','fsts','flds'):pass
        elif op=='fmfvrl':r[p[0]]=0 # converted output, irrelevant to addressing
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x46f48','--stop-address=0x46fb2',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text());cases=[]
    for length in (-3,-2,-1,0,1,2,3,255,256,511,512,513,1024):
        a=run(old,False,length);b=run(new,True,length);assert a==b,(length,a,b)
        half=int(length/2);expected_reads=[v for i in range(max(0,half)) for v in (0x20011000+2*i,0x20011000+2*(i+half))];expected_writes=[0x20012000+2*i for i in range(max(0,half))]
        assert a==(expected_reads,expected_writes);cases.append({'length':length,'outputs':len(a[1])})
    report={'cases':cases,'source_admitted':False,'limits':['Integer addressing, signed half-length and loop control only. FPU and stack value transfers omitted; per-iteration expression verified separately. This is not complete initializer execution.']}
    (ROOT/'docs/research/gx8002-imcra-normalization-indices.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify())
