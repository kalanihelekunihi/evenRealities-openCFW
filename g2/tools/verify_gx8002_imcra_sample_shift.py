# SPDX-License-Identifier: MIT
"""Decoded in-place shifts in the defined 0..31 shift-instruction domain."""
import json,re,subprocess,random
from build_gx8002_imcra_sample_shift import build,ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,entry,values,count,shift):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=0x20010000,r1=count&M,r2=shift&M);initial=r.copy();memory=[v&0xffff for v in values];trace=[];pc=entry;c=False
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(max(count,0)*15+30):
        op,args,width=code[pc];p=[a.strip() for a in args.split(',')];nxt=pc+width
        if op in ('bhz','blsz'):
            if (signed(r[p[0]])>0)==(op=='bhz'):nxt=int(p[1],0)
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addu','subu','subi'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=int(p[-1],0) if op=='subi' else r[p[-1]];r[p[0]]=(a+b if op=='addu' else a-b)&M
        elif op in ('ld.h','ld.hs'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*0x0\)',args);assert m,args
            reg,base=m.groups();index=(r[base]-0x20010000)//2;v=memory[index];trace.append(('read',index,v));r[reg]=v|0xffff0000 if op=='ld.hs' and v&0x8000 else v
        elif op=='sexth':r[p[0]]=r[p[1]]|0xffff0000 if r[p[1]]&0x8000 else r[p[1]]&0xffff
        elif op in ('lsl','asr'):
            amount=r[p[1]];assert 0<=amount<=31
            r[p[0]]=((r[p[0]]<<amount) if op=='lsl' else signed(r[p[0]])>>amount)&M
        elif op=='stbi.h':
            m=re.fullmatch(r'(r\d+),\s*\((r\d+)\)',args);assert m,args
            reg,base=m.groups();index=(r[base]-0x20010000)//2;memory[index]=r[reg]&0xffff;trace.append(('write',index,memory[index]));r[base]+=2
        elif op=='cmpne':c=r[p[0]]!=r[p[1]]
        elif op=='bt':
            if c:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return memory,trace
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x46bcc','--stop-address=0x46c04',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-imcra-sample-shift/index.disassembly.txt').read_text());cases=0
    def check(values,count,shift):
        nonlocal cases
        a=execute(old,0x46bcc,values,count,shift);b=execute(new,0x1000e28c,values,count,shift);assert a==b
        expected=[v&0xffff for v in values]
        for i in range(max(0,count)):expected[i]=((values[i]>>shift) if shift>0 else values[i]<<-shift)&0xffff
        assert a[0]==expected and len(a[1])==max(0,count)*2;cases+=1
    for sample in range(-32768,32768):
        for shift in (-15,0,1):check([sample],1,shift)
    for shift in range(-31,32):
        check([-32768,-32767,-1,0,1,16384,32767],7,shift)
        for count in (-2147483648,-1,0):check([],count,shift)
    rng=random.Random(0x46bcc)
    for count in (2,3,255,256,512):
        for shift in (-31,-15,-1,0,1,15,31):check([rng.randrange(-32768,32768) for _ in range(count)],count,shift)
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Decoded shifts limited to magnitudes <=31; every int16 value tested at shifts -15,0,1, plus all shifts -31..31 on extrema and seeded arrays. Exact reads/writes, final memory, saved ABI and no accesses for nonpositive counts. Larger shift-count ISA behavior is retained by source assembly but not qualified here.']}
    (ROOT/'docs/research/gx8002-imcra-sample-shift-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
