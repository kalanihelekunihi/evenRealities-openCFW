# SPDX-License-Identifier: MIT
"""Decoded eight-pin setup call order and original terminal paths."""
import json,subprocess
from itertools import product
from build_gx8002_board_pin_setup_candidate import ROOT,build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
PINS=((5,0),(6,0),(11,0),(12,0),(7,3),(8,3),(9,3),(10,3))
ADDRESS=0x1020681c


def expected(results):
    trace=[('configure',p,f) for p,f in PINS]
    if sum(results)&MASK:
        return 'loop',trace+[('set',p,0) for p in (5,6,11,12)]+[('printf',0x1020ad66)]
    return 'returned',trace


def execute(code,entry,results,set_result=0,printf_result=0,configure_hook=None,set_hook=None,printf_hook=None):
    r={f'r{i}':(0x91370000+i*0x10203)&MASK for i in range(32)}
    r['r14']=0x2002f7fc;initial=r.copy();saved=None;pc=entry;trace=[];index=0
    for _ in range(150):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('Setup frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('Setup restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Setup ABI')
            if index!=8:raise ValueError('Setup incomplete call sequence')
            return 'returned',trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='br':
            nxt=int(args,0)
            if nxt==pc:
                if saved is None or index!=8:raise ValueError('Setup premature loop')
                return 'loop',trace
        elif op=='bsr':
            target=int(args,0)
            if entry==0xfda8:target=(target+0x101f6a74)&MASK
            if target==0x102067dc:
                if index>=len(results):raise ValueError('Setup excess configure call')
                trace.append(('configure',r['r0'],r['r1']));value=results[index];index+=1
                if configure_hook is not None:value=configure_hook(r['r0'],r['r1'])
            elif target==0x102065dc:
                trace.append(('set',r['r0'],r['r1']));value=set_result
                if set_hook is not None:value=set_hook(r['r0'],r['r1'])
            elif target==0x10206c24:
                trace.append(('printf',r['r0']));value=printf_result
                if printf_hook is not None:value=printf_hook(r['r0'])
            else:raise ValueError('Setup helper target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xa1790000+i
            r['r0']=value
        else:raise ValueError('Setup instruction '+op)
        pc=nxt
    raise ValueError('Setup bound')


def programs():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');out=ROOT/'build/gx8002-board'
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfda8','--stop-address=0xfe2c',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'board-pin-setup-candidate.disassembly.txt').read_text())
    return old,new


def verify():
    candidate=build();old,new=programs();count=0
    cases=list(product((0,MASK),repeat=8))+[(MASK,1,0,0,0,0,0,0),(0x80000000,0x80000000,0,0,0,0,0,0)]
    for results,set_result,printf_result in product(cases,(0,MASK),(0,37,MASK)):
        for code,entry in ((old,0xfda8),(new,ADDRESS)):
            if execute(code,entry,results,set_result,printf_result)!=expected(results):raise ValueError('Setup mismatch')
            count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Finite decoded calls and sum arithmetic with modeled helper returns. Self-branch is the original terminal error loop. Helper composition, shared nested stack, and hardware not qualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-board-pin-setup-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded board pin setup cases:',report['decoded_cases'])
