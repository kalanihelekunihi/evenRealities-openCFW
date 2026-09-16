# SPDX-License-Identifier: MIT
"""Decoded header/sizing rejection paths with modeled nonmutating helpers."""
import json,re,subprocess
from build_gx8002_backup_imcra_state import build,ROOT
from verify_gx8002_memcpy_source import decode
M=0xffffffff

def execute(code,entry,size):
    r={f'r{i}':0x70000000+i for i in range(32)};r.update(r0=48000,r1=0x20010000,r2=size,r14=0x8000);initial=r.copy();f={f'fr{i}':0x60000000+i for i in range(16)};initial_f=f.copy();mem={};trace=[];pc=entry;condition=False
    def store(a,v):
        mem[a]=v
        if a>=0x20010000:trace.append(('write',a,v))
    def signed(v):return v if v<0x80000000 else v-0x100000000
    for _ in range(160):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('push','pop'):
            regs=[]
            for part in p:
                if '-' in part:
                    a,b=part.split('-');regs.extend('r'+str(i) for i in range(int(a[1:]),int(b[1:])+1))
                else:regs.append(part)
            if op=='push':
                r['r14']-=len(regs)*4
                for i,reg in enumerate(regs):mem[r['r14']+i*4]=r[reg]
            else:
                for i,reg in enumerate(regs):r[reg]=mem[r['r14']+i*4]
                r['r14']+=len(regs)*4
                assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17))
                assert all(f[f'fr{i}']==initial_f[f'fr{i}'] for i in range(8,16))
                assert r['r0']==0;return trace
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsli'):
            a=r[p[0]] if len(p)==2 else r[p[1]];b=int(p[-1],0);r[p[0]]=((a+b) if op=='addi' else (a-b) if op=='subi' else a<<b)&M
        elif op in ('st.w','fsts','flds'):
            m=re.fullmatch(r'((?:fr|r)\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='flds':f[reg]=mem[a]
            else:store(a,(f if op=='fsts' else r)[reg])
        elif op=='fmtvrl':f[p[0]]=r[p[1]]
        elif op=='fmfvrl':r[p[0]]=f[p[1]]
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmplt':condition=signed(r[p[0]])<signed(r[p[1]])
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0)+(0x10000000-0x38940 if entry<0x10000000 else 0)
            if target==0x100100a4:trace.append(('power',f['fr0'],f['fr1']));result=0;float_result=0x3e809bcc
            elif target==0x1000e314:trace.append(('workspace',r['r0'],r['r1']));result=42124;float_result=0xdeadbeef
            elif target==0x10009934:trace.append(('printf',r['r0'],r['r1'],r['r2']));result=0;float_result=0xdeadbeef
            else:raise AssertionError(hex(target))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
            for i in range(8):f[f'fr{i}']=0xdead1000+i
            r['r0']=result;f['fr0']=float_result
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');raw=subprocess.check_output([pre,'-D','--start-address=0x46cc4','--stop-address=0x470c4',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True);stock=decode(raw);source=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text())
    sizes=list(range(197))+[1024,38219,38220,42318,42319,0x80000000,0xfffffffe,M]
    for size in sizes:
        a=execute(stock,0x46cc4,size);b=execute(source,0x1000e384,size);assert a==b,(size,a,b)
        assert a[-1]==('printf',0x100142c4 if size<196 else 0x10014310,size,196 if size<196 else 42320)
        if size<196:assert len(a)==1
    report={'build':evidence,'cases':len(sizes),'source_admitted':False,'limits':['Header and signed sizing rejection paths only, ordered state writes/calls and saved ABI. Power and sizing helpers are modeled with caller clobbers and no state mutation; accepted paths and full algorithm unverified.']}
    (ROOT/'docs/research/gx8002-imcra-initializer-rejection.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
