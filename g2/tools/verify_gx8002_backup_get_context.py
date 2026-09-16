# SPDX-License-Identifier: MIT
"""Decoded backup context selection and ordered word-store verification."""
import json,re,subprocess
from itertools import product
from build_gx8002_backup_get_context import build,ROOT,Elf32,sha,IMAGE_SHA
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,entry,index,output,size_output,seed):
    r={f'r{i}':(seed+i)&MASK for i in range(32)};r.update(r0=index,r1=output,r2=size_output);initial=r.copy();trace=[]
    for _ in range(40):
        op,args,width=code[entry];p=[x.strip() for x in args.split(',')]
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('andi','mult','addi','addu','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a&b if op=='andi' else a*b if op=='mult' else a<<b if op=='lsli' else a+b)&MASK
        elif op=='st.w':
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();trace.append(((r[base]+int(off,0))&MASK,r[reg]))
        elif op=='str.w':
            reg,base,index_reg,shift=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args).groups();trace.append(((r[base]+(r[index_reg]<<int(shift)))&MASK,r[reg]))
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],trace
        else:raise AssertionError((op,args))
        entry+=width
    raise AssertionError('Instruction bound')

def verify():
    candidate=build();assert candidate['fits'];out=ROOT/'build/gx8002-backup-get-context'
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock');assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x427cc','--stop-address=0x42800',str(wrapper)],text=True));new=decode((out/'index.disassembly.txt').read_text());cases=0
    for index,seed in product((*range(256),0x7fffffff,0x80000000,0xfffffffc,MASK),(0,0xabcdef00)):
        slot=0x20017780+(index&3)*2816
        for output,size_output in product((0x20050000,slot,slot+16),(0x20050004,0x20050000,slot,slot+16)):
            a=execute(old,0x427cc,index,output,size_output,seed);b=execute(new,0x10009e8c,index,output,size_output,seed)
            wanted=(0,[(slot,0x20017700),(slot+16,slot+32),(output,slot),(size_output,2816)])
            assert a==b==wanted;cases+=1
    result={'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'limits':['Exact ordered word stores and saved ABI verified; four context slots and wrapping index boundaries covered.', 'Output-address overlap cases qualify generated machine-store ordering, not arbitrary C aliasing or invalid pointer use. No hardware qualification.']}
    (ROOT/'docs/research/gx8002-backup-get-context-verification.json').write_text(json.dumps(result,indent=2)+'\n');return result
if __name__=='__main__':print(verify()['decoded_cases'])
