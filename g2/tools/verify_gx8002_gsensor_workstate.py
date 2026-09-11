# SPDX-License-Identifier: MIT
"""Decoded gsensor diagnostic accessor; state may change during printf."""
import json,re,subprocess
from itertools import product
from build_gx8002_gsensor_workstate_candidate import ROOT,build
from verify_gx8002_memcpy_source import decode
ADDRESS=0x10206908


def expected(before,after):
    return [('read',0x20026c70,before),('printf',0x1020adaa,before),('read',0x20026c70,after)],after


def execute(code,entry,before,after,printf_result,printf_hook=None):
    r={f'r{i}':0x91730000+i for i in range(32)};r['r14']=0x2002f7fc
    initial=r.copy();saved=None;pc=entry;trace=[];printed=False
    for _ in range(20):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('State frame')
            saved=(r['r4'],r['r15']);r['r14']-=8
        elif op=='pop':
            if args!='r4, r15' or saved is None:raise ValueError('State restore')
            r['r4'],r['r15']=saved;r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('State ABI')
            return trace,r['r0']
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('State load operand')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if address!=0x20026c70:raise ValueError('State address')
            value=after if printed else before;r[reg]=value;trace.append(('read',address,value))
        elif op=='bsr':
            if int(args,0)!=(0x101b0 if entry==0xfe94 else 0x10206c24) or printed:raise ValueError('State printf target/count')
            trace.append(('printf',r['r0'],r['r1']));printed=True
            if printf_hook is not None:printf_result=printf_hook(r['r0'],r['r1'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xa9170000+i
            r['r0']=printf_result
        else:raise ValueError('State instruction '+op)
        pc+=width
    raise ValueError('State bound')


def programs():
    out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xfe94','--stop-address=0xfeac',str(out/'padmux-get-stock.elf')],text=True))
    new=decode((out/'gsensor-workstate-candidate.disassembly.txt').read_text());return old,new


def verify():
    candidate=build();old,new=programs();count=0
    for before,after,result in product((0,1,2,0x7fffffff,0x80000000,0xffffffff),(0,1,2,0x7fffffff,0x80000000,0xffffffff),(0,37,0xffffffff)):
        for code,entry in ((old,0xfe94),(new,ADDRESS)):
            if execute(code,entry,before,after,result)!=expected(before,after):raise ValueError('State decoded mismatch')
            count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Finite before/after state values with printf return/clobbers modeled. State lifecycle, nested printf and physical hardware not qualified.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-gsensor-workstate-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Gsensor state decoded cases:',report['decoded_cases'])
