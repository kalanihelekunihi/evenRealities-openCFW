# SPDX-License-Identifier: MIT
"""Decoded peak helper comparison: sample extrema, scan ordering and ABI."""
import json,re,subprocess,random
from build_gx8002_imcra_peak_shift import build,ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,entry,samples,count):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=0x20010000,r1=count&M);initial=r.copy();reads=[];pc=entry;c=False
    def signed(x):return x if x<0x80000000 else x-0x100000000
    for _ in range(10000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.h','ld.hs','ldbi.hs'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)(?:,\s*(0x[0-9a-f]+|\d+))?\)',args);assert m,args
            reg,base,offset=m.groups();a=r[base]+int(offset or '0',0);index=(a-0x20010000)//2;assert a%2==0 and 0<=index<len(samples)
            value=samples[index]&0xffff;reads.append(index)
            r[reg]=value|0xffff0000 if op!='ld.h' and value&0x8000 else value
            if op=='ldbi.hs':r[base]+=2
        elif op=='sexth':r[p[0]]=r[p[1]]|0xffff0000 if r[p[1]]&0x8000 else r[p[1]]&0xffff
        elif op=='zexth':r[p[0]]=r[p[1]]&0xffff
        elif op=='abs':r[p[0]]=abs(signed(r[p[1]]))
        elif op=='ff1':assert r[p[1]];r[p[0]]=32-r[p[1]].bit_length()
        elif op in ('max.s32','max.u32'):r[p[0]]=max(r[p[1]],r[p[2]],key=signed if op=='max.s32' else lambda x:x)
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addu','subu','addi','subi','and','lsri','lsr'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=int(p[-1],0) if op in ('addi','subi','lsri') else r[p[-1]]
            r[p[0]]=((a+b) if op in ('addu','addi') else a-b if op in ('subu','subi') else a&b if op=='and' else a>>b)&M
        elif op=='cmplti':c=signed(r[p[0]])<int(p[1],0)
        elif op=='cmplt':c=signed(r[p[0]])<signed(r[p[1]])
        elif op=='cmpne':c=r[p[0]]!=r[p[1]]
        elif op=='cmpnei':c=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf'):
            if c==(op=='bt'):nxt=int(args,0)
        elif op=='bez':
            if not r[p[0]]:nxt=int(p[1],0)
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&M
            if r[p[0]]:nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],reads
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x46c04','--stop-address=0x46c54',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-imcra-peak-shift/index.disassembly.txt').read_text());cases=0
    def check(samples,count):
        nonlocal cases
        a=execute(old,0x46c04,samples,count);b=execute(new,0x1000e2c4,samples,count);assert a==b,(samples,count,a,b)
        consumed=samples[:max(1,count)];peak=max(abs(v) for v in consumed);expected=peak.bit_length()-15 if peak else -15
        assert a==(expected&M,list(range(max(1,count))));cases+=1
    for sample in range(-32768,32768):check([sample],1)
    for sample in (-32768,-1,0,1,32767):
        for count in (-2147483648,-1,0):check([sample],count)
    rng=random.Random(0x46c04)
    for length in (2,3,16,255,256,512):
        for _ in range(24):check([rng.randrange(-32768,32768) for _ in range(length)],length)
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Every individual int16 value plus seeded scans and nonpositive counts; readable sample zero required. Exact ordered loads, return and saved ABI checked. ff1 modeled as CLZ per GCC csky.md clzsi2 mapping; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-imcra-peak-shift-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
