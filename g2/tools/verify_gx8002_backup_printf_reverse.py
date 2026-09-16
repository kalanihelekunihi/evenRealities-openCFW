# SPDX-License-Identifier: MIT
"""Decoded reverse/padding callback traces against stock and an oracle."""
import itertools,json,re,subprocess
from build_gx8002_backup_printf_reverse import build,ROOT,Elf32,sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,pc,data,idx,width,flags,maxlen):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=0x12345678,r1=0x20040000,r2=idx,r3=maxlen,r14=0x20070000);initial=r.copy();mem={0x20070000+i*4:v for i,v in enumerate((0x20050000,len(data),width,flags))};saved=None;condition=False;events=[]
    for _ in range(10000):
        op,args,n=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+n
        if op=='push':
            assert args=='r4-r11, r15, r16-r17';saved={i:r[f'r{i}'] for i in (*range(4,12),15,16,17)};r['r14']-=44
        elif op=='pop':
            assert args=='r4-r11, r15, r16-r17';r['r14']+=44
            for i,v in saved.items():r[f'r{i}']=v
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],events
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0);r[p[0]]=(a+(b if op=='addi' else -b))&M
        elif op in ('addu','subu'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]];r[p[0]]=(a+(b if op=='addu' else -b))&M
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&M
        elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op in ('cmpne','cmphs'):condition=(r[p[0]]!=r[p[1]]) if op=='cmpne' else r[p[0]]>=r[p[1]]
        elif op in ('br','bt','bf'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(p[0],0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op in ('ld.w','st.w','ld.b'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=(r[base]+int(off,0))&M
            if op=='st.w':mem[a]=r[reg]
            elif op=='ld.w':r[reg]=mem[a]
            else:r[reg]=data[a-0x20050000]
        elif op=='ldr.b':
            reg,base,index,shift=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args).groups();r[reg]=data[((r[base]+(r[index]<<int(shift)))&M)-0x20050000]
        elif op=='jsr':
            assert r[args]==0x12345678;events.append(tuple(r[f'r{i}'] for i in range(4)))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
        else:raise ValueError((op,args))
        pc=nxt
    raise AssertionError('execution bound')

def verify():
    evidence=build();path=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(path.read_bytes(),'stock');assert sha(e.contents(next(s for s in e.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0x41344','--stop-address=0x413e0',str(path)],text=True));new=decode((ROOT/'build/gx8002-backup-printf/reverse.disassembly.txt').read_text());cases=0
    for length,width,flags,idx,maxlen in itertools.product((0,1,2,8,32),(0,1,2,7,8,9,33),(0,1,2,3,0x400),(0,7,M-2,M),(0,1,16,M)):
        data=bytes((i*73+128)&255 for i in range(length));chars=([32]*max(0,width-length) if not flags&3 else [])+list(data[::-1])
        if flags&2:chars += [32]*max(0,width-len(chars))
        expected=((idx+len(chars))&M,[(c,0x20040000,(idx+i)&M,maxlen) for i,c in enumerate(chars)])
        assert execute(old,0x41344,data,idx,width,flags,maxlen)==execute(new,0x10008a04,data,idx,width,flags,maxlen)==expected,(length,width,flags,idx,maxlen)
        cases+=1
    report={'build':evidence,'cases':cases,'limits':['Finite lengths/widths, callback modeled without source mutation; exact callback arguments, return and ABI checked. Integration pending.'],'source_admitted':False}
    (ROOT/'docs/research/gx8002-backup-printf-reverse-execution.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
