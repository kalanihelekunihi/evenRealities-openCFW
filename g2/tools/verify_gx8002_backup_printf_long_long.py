# SPDX-License-Identifier: MIT
"""Decoded integer digit generation against stock and an independent oracle."""
import itertools,json,re,subprocess
from build_gx8002_backup_printf_long_long import build,ROOT,Elf32,sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,pc,delta,value,base,negative,prec,width,flags,arithmetic=None):
    idx=7;maxlen=64
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=0x12345678,r1=0x20040000,r2=idx,r3=maxlen,r14=0x20070000);initial=r.copy();mem={0x20070000+i*4:v for i,v in enumerate((value&M,value>>32,negative,base&M,base>>32,prec,width,flags))};saved=None;condition=False;events=[]
    for _ in range(10000):
        op,args,n=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+n
        if op=='push':
            assert args=='r4-r11, r15, r16-r17';saved={i:r[f'r{i}'] for i in (*range(4,12),15,16,17)};r['r14']-=44
        elif op=='pop':
            r['r14']+=len(saved)*4
            for i,v in saved.items():r[f'r{i}']=v
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],events
        elif op=='or':r[p[0]]=(r[p[1]]|r[p[2]]) if len(p)==3 else r[p[0]]|r[p[1]]
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+(b if op=='addi' else -b))&M
        elif op in ('addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+(b if op=='addu' else -b))&M
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&M
        elif op in ('andi','andni','bclri'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=a & (b if op=='andi' else ~(1<<b) if op=='bclri' else ~b)
        elif op=='divu':r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='mult':r[p[0]]=(r[p[1]]*r[p[2]])&M
        elif op=='incf':
            if not condition:r[p[0]]=(r[p[1]]+int(p[2],0))&M
        elif op in ('cmpnei','cmphsi'):condition=r[p[0]]!=int(p[1],0) if op=='cmpnei' else r[p[0]]>=int(p[1],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('cmpne','cmphs'):condition=(r[p[0]]!=r[p[1]]) if op=='cmpne' else r[p[0]]>=r[p[1]]
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(p[0],0)
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&M
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('ld.w','st.w','ld.b','st.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&M
            if op=='st.w':mem[a]=r[reg]
            elif op=='st.b':mem[a]=r[reg]&255
            elif op=='ld.w':r[reg]=mem[a]
            else:r[reg]=mem[a]&255
        elif op=='stbi.b':
            reg,b=re.fullmatch(r'(r\d+), \((r\d+)\)',args).groups();mem[r[b]]=r[reg]&255;r[b]=(r[b]+1)&M
        elif op=='bsr':
            target=int(args,0)+delta
            if target in (0x1001149c,0x100117d0):
                numerator=r['r0']|(r['r1']<<32);denominator=r['r2']|(r['r3']<<32)
                result=(arithmetic(target,numerator,denominator) if arithmetic else
                        divmod(numerator,denominator)[0 if target==0x1001149c else 1])
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
                r['r0']=result&M;r['r1']=result>>32;pc=nxt;continue
            assert int(args,0)+delta==0x10008aa0
            a=r['r14'];buf=mem[a];length=mem[a+4]
            events.append((tuple(r[f'r{i}'] for i in range(4)),bytes(mem[buf+i] for i in range(length)),tuple(mem[a+4*i] for i in range(2,7))))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            r['r0']=123
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def oracle(value,base,negative,precision,width,flags):
    effective_flags=flags if value else flags&~16
    # Python formatting provides an independent conversion for supported bases.
    spec={2:'b',8:'o',10:'d',16:'X' if flags&32 else 'x'}[base]
    digits=b'' if not value and flags&1024 else format(value,spec)[::-1][:32].encode('ascii')
    return 123,[((0x12345678,0x20040000,7,64),digits,(negative,base,precision,width,effective_flags))]

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');path=ROOT/'build/gx8002-board/padmux-get-stock.elf'
    stock=Elf32(path.read_bytes(),'stock');assert sha(stock.contents(next(s for s in stock.sections if s['name']=='.data')))==IMAGE_SHA
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x41688','--stop-address=0x41760',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-printf/long-long.disassembly.txt').read_text());cases=0
    for v,b,n,p,w,f in itertools.product((0,1,9,10,255,M,M+1,1<<63,(1<<64)-1),(2,8,10,16),(0,1),(0,1,8),(0,16),(0,16,32,1024,1040,1056)):
        a=execute(old,0x41688,0x10000000-0x38940,v,b,n,p,w,f);z=execute(new,0x10008d48,0,v,b,n,p,w,f)
        assert a==z==oracle(v,b,n,p,w,f),(v,b,n,p,w,f,a,z);cases+=1
    report={'build':evidence,'cases':cases,'limits':['Formatter and exact nonzero division/remainder modeled; finite bases and values, digit buffer and callee arguments compared. Independent digit oracle passes; integration pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-printf-long-long-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
