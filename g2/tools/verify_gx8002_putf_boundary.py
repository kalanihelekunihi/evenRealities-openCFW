# SPDX-License-Identifier: MIT
"""Decoded putf stream/character forwarding and EOF normalization."""
import json
import subprocess
from itertools import product
from compare_gx8002_format import ROOT, decode
MASK=0xffffffff


def execute(code,start,target,stream,character,result,fputc_hook=None):
    r={f'r{i}':0x91730000+i for i in range(32)}
    r.update(r0=stream,r1=character)
    initial=r.copy();saved=None;pc=start;condition=False;calls=[]
    for _ in range(30):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('putf frame')
            saved=r['r15']
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('putf restore')
            r['r15']=saved
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('putf ABI')
            return r['r0'],calls
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='bsr':
            if int(args,0)!=target:raise ValueError('putf target')
            calls.append((r['r0'],r['r1']))
            if fputc_hook is not None:result=fputc_hook(r['r0'],r['r1'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xa5170000+i
            r['r0']=result
        else:raise ValueError('putf instruction '+op)
        pc=nxt
    raise ValueError('putf bound')


def programs():
    out=ROOT/'build/gx8002-tinyprintf';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xff24','--stop-address=0xff3c',str(out/'stock.elf')],text=True))
    new=decode(subprocess.check_output([pre,'-d','--section=.text.putf',str(out/'formatter.elf')],text=True))
    return old,new


def verify():
    old,new=programs();count=0
    for stream,character,result in product((0,0x3000,MASK),(0,10,13,127,255,256,MASK),(0,1,255,0x80000000,MASK)):
        want=(int(result!=MASK),[(character,stream)])
        for code,start,target in ((old,0xff24,0x101fc),(new,0x10206998,0x10206c70)):
            if execute(code,start,target,stream,character,result)!=want:raise ValueError('putf mismatch')
            count+=1
    return {'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Finite putf forwarding and EOF result checks with saved-register model. fputc return and physical UART modeled. Existing artifacts read only.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-putf-boundary.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded putf cases:',report['decoded_cases'])
