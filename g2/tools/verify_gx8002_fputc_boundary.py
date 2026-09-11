# SPDX-License-Identifier: MIT
"""Decoded libc console wrapper: forwards character, ignores console result."""
import json
import subprocess
from itertools import product
from compare_gx8002_format import ROOT,decode


def execute(code,start,target,character,stream,console_result,console_hook=None):
    r={f'r{i}':0x91370000+i for i in range(32)}
    r.update(r0=character,r1=stream);initial=r.copy();saved=None;pc=start;calls=[]
    for _ in range(10):
        op,args,width=code[pc]
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('fputc frame')
            saved=r['r15']
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('fputc restore')
            r['r15']=saved
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('fputc ABI')
            return r['r0'],calls
        elif op=='movi':
            reg,value=args.split(', ');r[reg]=int(value,0)
        elif op=='bsr':
            if int(args,0)!=target:raise ValueError('fputc target')
            calls.append(r['r0'])
            if console_hook is not None:console_hook(r['r0'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xa1790000+i
            r['r0']=console_result
        else:raise ValueError('fputc instruction '+op)
        pc+=width
    raise ValueError('fputc bound')


def programs():
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x101fc','--stop-address=0x10206',str(ROOT/'build/gx8002-tinyprintf/stock.elf')],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-fputc/fputc.elf')],text=True))
    return old,new


def verify():
    old,new=programs();count=0
    for character,stream,result in product((0,10,13,255,256,0xffffffff),(0,0x3000,0xffffffff),(0,1,0xffffffff)):
        for code,start,target in ((old,0x101fc,0xcd7c),(new,0x10206c70,0x102037f0)):
            if execute(code,start,target,character,stream,result)!=(0,[character]):raise ValueError('fputc mismatch')
            count+=1
    return {'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded fputc wrapper; console call modeled with caller clobbers. No UART timing or hardware qualification.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-fputc-boundary.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded fputc cases:',report['decoded_cases'])
