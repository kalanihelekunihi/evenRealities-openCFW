#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare full dispatcher execution and ordered caller-record/MMIO accesses."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_platform_read import build,ROOT,IMAGE,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,pc,delta,table,operation,events,record=0x20028000,write_hook=None):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=operation,r1=record)
    initial=r.copy();carry=None;index=0
    def effect(kind,address,value=None):
        nonlocal index
        if index>=len(events):raise ValueError('extra memory effect')
        e=events[index];index+=1
        if e[:2]!=[kind,address] or value is not None and e[2]!=value:raise ValueError('memory effect mismatch')
        if write_hook and kind.startswith('write'):write_hook(address,int(kind[5:]),value)
        return e[2]
    for step in range(160):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mvc':
            if carry is None:raise ValueError('undefined carry')
            r[p[0]]=int(carry)
        elif op in ('zexth','zextb'):r[p[0]]=r[p[1]]&(65535 if op=='zexth' else 255)
        elif op in ('lsli','rotli','subi','andi','or'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else (a<<b)|(a>>(32-b)) if op=='rotli' else a-b if op=='subi' else a&b if op=='andi' else a|b)&0xffffffff
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op=='ldr.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args)
            if not m or r[m[2]]!=0x100249cc or r[m[3]]>=10:raise ValueError('invalid dispatch lookup')
            r[m[1]]=table[r[m[3]]]
        elif op in ('ld.b','ld.h','ld.w','st.w','st.h','st.b','ldbi.h','stbi.w'):
            post=op in ('ldbi.h','stbi.w')
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args) if post else re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown memory address')
            reg,base=m[1],m[2];a=(r[base]+(0 if post else int(m[3],0)))&0xffffffff
            if op.startswith('ld'):r[reg]=effect('read'+('8' if op=='ld.b' else '16' if op in ('ld.h','ldbi.h') else '32'),a)
            else:
                bits=8 if op=='st.b' else 16 if op=='st.h' else 32
                effect('write'+str(bits),a,r[reg]&((1<<bits)-1))
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
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,18))):raise ValueError('return state mismatch')
            return r['r0']
        else:raise ValueError('unknown config instruction '+op)
        pc=n
    raise ValueError('execution bound exceeded')

def oracle(operation,values,record=0x20028000):
    events=[]
    def read(address):
        value=values[address];events.append(['read32',address,value]);return value
    def write(offset,bits,value):events.append(['write'+str(bits),(record+offset)&0xffffffff,value&((1<<bits)-1)])
    if operation==0:
        for i in range(6):write(i*2,16,read(0xa0000004+i*4))
        a=read(0xa000001c);b=read(0xa0000020);write(12,16,a);write(14,16,b)
    elif operation in (1,2,3,4,6,8,9):
        address={1:0xa0000024,2:0xa0000028,3:0xa000002c,4:0xa0000034,6:0xa0000030,8:0xa0000038,9:0x20027314}[operation]
        value=read(address);write(0,32,value&15 if operation in (3,4) else value)
    elif operation==5:write(0,8,read(0xa0010058)&1);write(4,32,read(0xa001005c))
    elif operation==7:
        packed=read(0xa0000048);write(0,8,read(0xa0000040)&1);write(1,8,read(0xa0000044));write(4,16,read(0xa000004c));write(2,8,packed&15);write(3,8,(packed>>4)&15);write(6,8,read(0xa0000050));write(7,8,read(0xa0000054))
    return events

def verify():
    candidate=build();directory=ROOT/'build/gx8002-board';path=directory/'padmux-get-stock.elf'
    from analyze_gx8002_upstream_objects import sha,IMAGE_SHA
    stock=IMAGE.read_bytes();elf=Elf32(path.read_bytes(),'stock');assert sha(stock)==IMAGE_SHA and sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x16824','--stop-address=0x168e0',str(path)],text=True));new=decode((directory/'platform-read-linked.disassembly.txt').read_text())
    linked=Elf32((directory/'platform-read.elf').read_bytes(),'getter');section=next(s for s in linked.sections if s['name']=='.rodata.platform_read')
    old_table=struct.unpack_from('<10I',stock,0x169e0);new_table=struct.unpack('<10I',linked.contents(section));cases=0
    for operation in (*range(12),0x80000000,0xffffffff):
        for seed in (0,0xffffffff,0xaaaaaaaa,0x55555555,*[1<<i for i in range(32)]):
            addresses=[*range(0xa0000004,0xa0000058,4),0xa0010058,0xa001005c,0x20027314]
            values={a:(seed^(i*0x1020304))&0xffffffff for i,a in enumerate(addresses)}
            events=oracle(operation,values);wanted=0 if operation<10 else 0xffffffff
            assert execute(old,0x16824,0x1000dfec,old_table,operation,events)==execute(new,0x10024810,0,new_table,operation,events)==wanted
            cases+=1
    relocated=0
    for record in (0x20028004,0x2006fff0,0xfffffffc):
        for operation in (*range(10),0xffffffff):
            values={a:0x87654321 for a in addresses};events=oracle(operation,values,record)
            wanted=0 if operation<10 else 0xffffffff
            assert execute(old,0x16824,0x1000dfec,old_table,operation,events,record)==execute(new,0x10024810,0,new_table,operation,events,record)==wanted
            relocated+=1
    return {'candidate':candidate,'cases':cases,'relocated_record_cases':relocated,'source_admitted':False,'limits':['Ordered decoded MMIO reads and output access widths/values and ABI checked; register values scripted, three additional aligned record addresses checked, including 32-bit address wrap; mapped-memory validity not established. Candidate fits its slot but remains unregistered; no hardware qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-platform-read-comparison.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
