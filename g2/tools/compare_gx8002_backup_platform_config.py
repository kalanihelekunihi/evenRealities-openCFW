#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare full dispatcher execution and ordered caller-record/MMIO accesses."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_backup_platform_config import build,ROOT,IMAGE,Elf32
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
        elif op in ('lsli','rotli','subi','andi','or'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else (a<<b)|(a>>(32-b)) if op=='rotli' else a-b if op=='subi' else a&b if op=='andi' else a|b)&0xffffffff
        elif op=='ldr.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args)
            if not m or r[m[2]]!=0x10012a3c or r[m[3]]>=10:raise ValueError('invalid dispatch lookup')
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
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,18))):raise ValueError('return state mismatch')
            return r['r0']
        else:raise ValueError('unknown config instruction '+op)
        pc=n
    raise ValueError('execution bound exceeded')


def oracle(operation,data,second):
    events=[]
    def read(offset,size):
        value=int.from_bytes(data[offset:offset+size],'little');events.append(['read'+str(size*8),0x20028000+offset,value]);return value
    def write(address,value):events.append(['write',address,value])
    if operation==0:
        for i in range(8):write(0xa0000004+i*4,read(i*2,2))
    elif operation in (1,2,3,4,8):write({1:0xa0000024,2:0xa0000028,3:0xa000002c,4:0xa0000034,8:0xa0000038}[operation],read(0,4))
    elif operation==5:
        write(0xa0010058,read(0,1)&1);write(0xa001005c,read(4,4))
    elif operation==7:
        packed=read(3,1)<<4;packed|=read(2,1)
        second=read(1,1);first=read(0,1);period=read(4,2)
        write(0xa000004c,period);write(0xa0000048,packed)
        write(0xa0000044,int(second!=0));write(0xa0000040,int(first!=0))
    elif operation==9:
        write(0xa000003c,read(0,4)&1)
        events.append(['read32',0x20028000,second]);write(0x20017398,second&1)
    else:return 0xffffffff,events
    return 0,events


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-backup-platform-config';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'config-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x4e08c','--stop-address=0x4e170',str(wrapper)],text=True))
    new=decode((out/'config-linked.disassembly.txt').read_text())
    oldtable=struct.unpack_from('<10I',IMAGE.read_bytes(),0x4b37c)
    elf=Elf32((out/'config.elf').read_bytes(),'config');sec=next(s for s in elf.sections if s['name']=='.rodata.platform_config')
    newtable=struct.unpack('<10I',elf.contents(sec));cases=0
    for operation in (*range(12),0x7fffffff,0x80000000,0xffffffff):
        for seed in range(256):
            data=bytes((seed+i*71)&255 for i in range(16))
            for second in (0,1,0xffffffff):
                result,events=oracle(operation,data,second)
                if execute(old,0x4e08c,(0x10003000-0x3b940),oldtable,operation,events)!=result or execute(new,0x1001574c,0,newtable,operation,events)!=result:raise ValueError('dispatcher mismatch')
                cases+=1
    for high in range(256):
        for low in range(256):
            data=bytes([high&1,low&1,low,high,0xff,0x80])+bytes(10)
            result,events=oracle(7,data,0)
            if execute(old,0x4e08c,(0x10003000-0x3b940),oldtable,7,events)!=result or execute(new,0x1001574c,0,newtable,7,events)!=result:raise ValueError('packed-byte mismatch')
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Aligned caller records and ordered record/register effects; no physical hardware qualification.'],
            'coverage':['Every operation; invalid unsigned selectors; every byte value at every record offset.', 'All 65536 independent packed-byte pairs in operation 7.', 'Operation 9 second read can differ independently from the first; source-generated dispatch table executed.']}
    (ROOT/'docs/research/gx8002-backup-platform-config-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
