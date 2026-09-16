# SPDX-License-Identifier: MIT
"""Compare decoded float-one array writes for observed positive bin counts."""
import json,re,subprocess
from build_gx8002_backup_imcra_state import ROOT
from verify_gx8002_memcpy_source import decode

def run(code,source,bins):
    first=0x20018000;second=0x2001a000;r={f'r{i}':0 for i in range(32)}
    r.update(r2=bins,r4=0x20010000,r1=first,r8=first+4*bins,r7=second,r0=second+4*bins)
    pc=0x1000e56a if source else 0x46e9a;end=0x1000e586 if source else 0x46eb8;writes=[];condition=False
    for _ in range(20000):
        if pc==end:return writes
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='addi':r[p[0]]+=int(p[-1],0)
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmplt':condition=r[p[0]]<r[p[1]]
        elif op=='blsz':
            if r[p[0]]<=0:nxt=int(p[1],0)
        elif op=='bt':
            if condition:nxt=int(args,0)
        elif op=='br':nxt=int(args,0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+),\s*\((r\d+),\s*(0x[0-9a-f]+|\d+)\)',args);assert m,args
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='ld.w':r[reg]={0x200100a8:first,0x20010098:second}[a]
            else:writes.append((a,r[reg]))
        else:raise AssertionError((hex(pc),op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x46e9a','--stop-address=0x46eb8',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True));new=decode((ROOT/'build/gx8002-backup-imcra-state/state.disassembly.txt').read_text());cases=[]
    for bins in (0,1,2,255,256,257,511,512,513):
        a=run(old,False,bins);b=run(new,True,bins);assert a==b
        assert a==[(base+i*4,0x3f800000) for base in (0x20018000,0x2001a000) for i in range(bins)]
        cases.append({'bins':bins,'word_writes':len(a)})
    report={'cases':cases,'source_admitted':False,'limits':['Array fill block only, initialized pointer bindings and nonnegative counts. Exact ordered writes checked; prior allocation and subsequent floating setup are separate tests.']}
    (ROOT/'docs/research/gx8002-imcra-ones-arrays.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify())
