#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute nine-argument XIP setup against an ordered register-write oracle."""
import contextlib
import io
import itertools
import json
import random
import re
import struct
import subprocess
from build_gx8002_flash_xip import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,values):
    if len(values)!=9:raise ValueError('nine arguments required')
    r={f'r{i}':0x12340000+i for i in range(32)}
    r.update({f'r{i}':values[i] for i in range(4)})
    r['r14']=0x2002f7e8;initial=r.copy()
    stack={r['r14']+4*i:v for i,v in enumerate(values[4:])};trace=[];carry=None
    for step in range(150):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('lsli','lsri','rotli','subi','andi','or','bseti'):
            a=r[p[0] if len(p)==2 else p[1]]
            b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a>>b if op=='lsri' else (a<<b)|(a>>(32-b)) if op=='rotli' else a-b if op=='subi' else a&b if op=='andi' else a|b if op=='or' else a|(1<<b))&0xffffffff
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown memory address')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w':
                if address not in stack or address==initial['r14']+4:raise ValueError('unexpected argument read')
                r[reg]=stack[address]
            else:
                if address not in (0xa2000008,0xa2000114,0xa2000108,0xa200010c,0xa2000100,0xa2000104,0xa0300090):raise ValueError('unexpected register write')
                trace.append([address,r[reg]])
        elif op in ('cmpnei','cmpne','cmphsi'):
            a=r[p[0]];b=r[p[1]] if p[1].startswith('r') else int(p[1],0)
            carry=a>=b if op=='cmphsi' else a!=b
        elif op in ('bt','bf','br','bez','bnez'):
            if op in ('bt','bf') and carry is None:raise ValueError('undefined comparison')
            if op=='br' or op=='bt' and carry or op=='bf' and not carry or op in ('bez','bnez') and (r[p[0]]==0)==(op=='bez'):n=int(p[-1],0)
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,18),*range(22,32))):raise ValueError('preserved register mismatch')
            return r['r0'],trace
        else:raise ValueError('unsupported XIP instruction '+op)
        pc=n
    raise ValueError('execution bound exceeded')


def oracle(v):
    command,bits,cmd_width,address_bits,addr_width,unused,mode,wait,data_width=v
    writes=[[0xa2000008,0]]
    encoding={0:0,4:1,8:2,16:3}
    if bits not in encoding:return 0xffffffff,writes
    c,a,d=cmd_width//2,addr_width//2,data_width//2
    if c:
        if c!=d or a!=d:return 0xffffffff,writes
        transfer=2
    elif a:
        if a!=d:return 0xffffffff,writes
        transfer=1
    else:transfer=0
    if address_bits%4:return 0xffffffff,writes
    control=(wait*8192 | 0xc00000 | (address_bits//4)*16 | d | encoding[bits]*512 | transfer*4)&0xffffffff
    if mode==1:control|=0x08001000
    writes += [[0xa2000114,255],[0xa2000108,control],[0xa200010c,1],
               [0xa2000100,command],[0xa2000104,command],[0xa0300090,0],[0xa2000008,1]]
    return 0,writes


def vectors():
    for bits,c,a,d,addr,mode in itertools.product((0,1,3,4,7,8,9,15,16,17,0x80000000,0xffffffff),range(6),range(6),range(6),(0,3,4,24,0xffffffff),(0,1)):
        yield [235,bits,c,addr,a,0xfeedface,mode,4,d]
    base=[235,8,1,24,4,0,1,4,4]
    for index in range(9):
        for value in (0,1,2,3,4,0x7fffffff,0x80000000,0xffffffff,*[1<<b for b in range(32)]):
            v=base.copy();v[index]=value;yield v
    rng=random.Random(0x16380)
    for _ in range(2048):
        v=[rng.getrandbits(32) for _ in range(9)]
        v[1]=rng.choice((0,4,8,16));v[2]=0;v[4]=0;v[3]&=0xfffffffc
        yield v


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'xip-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x16380','--stop-address=0x16450',str(wrapper)],text=True))
    new=decode((out/'xip-linked.disassembly.txt').read_text());cases=0;success=0
    for v in vectors():
        expected=oracle(v)
        if execute(old,0x16380,v)!=expected or execute(new,0x1002436c,v)!=expected:raise ValueError('XIP mismatch '+repr(v))
        cases+=1;success+=expected[0]==0
    report={'build':evidence,'cases':cases,'successful_configurations':success,'rejected_configurations':cases-success,
            'limits':['Ordered MMIO and nine-argument ABI comparison; physical XIP hardware remains unqualified.'],
            'coverage':['Command length boundaries; all line-width triples 0..5; address alignment and mode branches.', 'All arguments individually cover each single bit and unsigned boundaries; 2048 seeded valid random configurations.']}
    (ROOT/'docs/research/gx8002-flash-xip-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases,success);return report

if __name__=='__main__':verify()
