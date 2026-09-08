#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare flash information selectors and ordered state/device reads."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_info import build,ROOT,IMAGE,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,pc,delta,table,operation,events):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=operation,r1=0x20028000)
    initial=r.copy();carry=None;index=0
    def effect(kind,address,value=None):
        nonlocal index
        if index>=len(events):raise ValueError('extra memory effect')
        e=events[index];index+=1
        if e[:2]!=[kind,address] or value is not None and e[2]!=value:raise ValueError('memory effect mismatch')
        return e[2]
    for step in range(160):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mvc':
            if carry is None:raise ValueError('undefined carry')
            r[p[0]]=int(carry)
        elif op in ('zexth','zextb'):r[p[0]]=r[p[1]]&(65535 if op=='zexth' else 255)
        elif op in ('lsli','lsri','rotli','subi','andi','or'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a>>b if op=='lsri' else (a<<b)|(a>>(32-b)) if op=='rotli' else a-b if op=='subi' else a&b if op=='andi' else a|b)&0xffffffff
        elif op=='ldr.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args)
            if not m or r[m[2]]!=0x1020be1c or r[m[3]]>=14:raise ValueError('invalid dispatch lookup')
            r[m[1]]=table[r[m[3]]]
        elif op in ('ld.b','ld.h','ld.w','st.w','ldbi.h','stbi.w'):
            post=op in ('ldbi.h','stbi.w')
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args) if post else re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown memory address')
            reg,base=m[1],m[2];a=r[base]+(0 if post else int(m[3],0))
            if op.startswith('ld'):r[reg]=effect('read'+('8' if op=='ld.b' else '16' if op in ('ld.h','ldbi.h') else '32'),a)
            else:effect('write',a,r[reg])
            if post:r[base]+=2 if op=='ldbi.h' else 4
        elif op in ('cmphsi','cmpnei'):
            carry=r[p[0]]>=int(p[1],0) if op=='cmphsi' else r[p[0]]!=int(p[1],0)
        elif op=='jmp':n=r[p[0]]-delta
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:n=int(p[1],0)
        elif op in ('bt','br'):
            if op=='bt' and carry is None:raise ValueError('undefined comparison')
            if op=='br' or carry:n=int(p[-1],0)
        elif op=='rts':
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('return state mismatch')
            return r['r0']
        else:raise ValueError('unknown config instruction '+op)
        pc=n
    raise ValueError('execution bound exceeded')

def oracle(selector,name,jedec,size):
    if selector in (1,2):return (name if selector==1 else jedec),[['read32',0x200264f0,0x20029000],['read32',0x20029000+(4 if selector==2 else 0),name if selector==1 else jedec]]
    if selector in (3,5,7,11):return (size if selector==3 else size>>12),[['read32',0x200264e8,size]]
    return {0:0,4:4096,6:4096,8:256,10:4096,12:0,13:1}.get(selector,0xffffffff),[]


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'info-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x1586c','--stop-address=0x16264',str(wrapper)],text=True))
    new=decode((out/'info-linked.disassembly.txt').read_text())
    oldtable=struct.unpack_from('<14I',IMAGE.read_bytes(),0x153a8)
    elf=Elf32((out/'info.elf').read_bytes(),'info');sec=next(s for s in elf.sections if s['name']=='.rodata.flash_info');newtable=struct.unpack('<14I',elf.contents(sec));cases=0
    for selector in (*range(16),0x7fffffff,0x80000000,0xffffffff):
        for size in (0,1,4095,4096,4097,0x3f000,0x7f000,0xff000,0x80000000,0xffffffff):
            for value in (0,0x1020be54,0x854012,0x80000000,0xffffffff):
                expected,events=oracle(selector,value,value,size)
                if execute(old,0x1586c,0x1000dfec,oldtable,selector,events)!=expected or execute(new,0x10023858,0,newtable,selector,events)!=expected:raise ValueError('getinfo mismatch')
                cases+=1
    for name in (0,1,0x1020be54,0x80000000,0xffffffff):
        expected,events=oracle(1,name,0,0)
        if execute(old,0x16258,0x1000dfec,oldtable,0,events)!=expected or execute(new,0x10024244,0,newtable,0,events)!=expected:raise ValueError('gettype mismatch')
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Valid selected device pointer for name/ID queries; state and device data remain retained.', 'No physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-flash-info-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
