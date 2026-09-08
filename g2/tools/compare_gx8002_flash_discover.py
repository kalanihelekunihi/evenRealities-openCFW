#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded discovery replay with ordered table/state effects and real frames."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_discover import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,delta,jedec,transport,events,seed):
    r={f'r{i}':(0x12340000+i+seed)&0xffffffff for i in range(32)}
    r['r14']=0x2002f7fc;initial=r.copy();saved=None;local={};carry=None;index=0;called=False
    def effect(kind,address,value=None):
        nonlocal index
        if index==len(events):raise ValueError('extra discovery effect')
        expected=events[index];index+=1
        if expected[:2]!=[kind,address] or value is not None and value!=expected[2]:raise ValueError('discovery effect mismatch')
        return expected[2]
    for step in range(1000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op=='push':
            if args!='r4-r5, r15' or saved is not None:raise ValueError('unknown discovery frame')
            saved=[r['r4'],r['r5'],r['r15']];r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None or r['r14']!=initial['r14']-12:raise ValueError('unbalanced discovery frame')
            r['r4'],r['r5'],r['r15']=saved;r['r14']+=12
            if index!=len(events) or not called or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('discovery return state mismatch')
            return r['r0']
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('lsli','addi','subi','addu','or','mult','mula.32.l'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a-b if op=='subi' else a|b if op=='or' else a*b if op=='mult' else r[p[0]]+a*b if op=='mula.32.l' else a+b)&0xffffffff
        elif op in ('ld.b','ld.h','ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown discovery address')
            reg,base,offset=m.groups();a=r[base]+int(offset,0)
            if op in ('ld.b','ld.h'):
                length=1 if op=='ld.b' else 2
                if any(a+i not in local for i in range(length)):raise ValueError('uninitialized JEDEC byte')
                r[reg]=sum(local[a+i]<<(8*i) for i in range(length))
            elif op=='ld.w':r[reg]=effect('read',a)
            else:effect('write',a,r[reg])
        elif op=='cmpne':carry=r[p[0]]!=r[p[1]]
        elif op in ('bt','br','bez','bnez','blz','bhsz'):
            if op=='bt' and carry is None:raise ValueError('undefined discovery comparison')
            take=op=='br' or op=='bt' and carry
            if op in ('bez','bnez'):take=(r[p[0]]==0)==(op=='bez')
            if op in ('blz','bhsz'):take=(r[p[0]]>=0x80000000)==(op=='blz')
            if take:n=int(p[-1],0)
        elif op=='bsr':
            if int(args,0)+delta!=0x10023684 or called:raise ValueError('unknown discovery call')
            if (r['r0'],r['r1'],r['r2'],r['r14'])!=(159,initial['r14']-16,3,initial['r14']-16):raise ValueError('JEDEC argument mismatch')
            called=True
            if transport<0x80000000:
                for i,v in enumerate(jedec.to_bytes(3,'big')):local[r['r1']+i]=v
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(0xa5a50000+seed+i)&0xffffffff
            r['r0']=transport
        else:raise ValueError('unknown discovery instruction '+op)
        pc=n
    raise ValueError('discovery execution bound exceeded')


def oracle(jedec,transport,table):
    base=0x200264e4;tb=0x20026624;events=[['write',base,0xffffffff]];selected=-1
    if transport>=0x80000000:return 0xffffffff,events
    def scan(wanted):
        for i,(identifier,size) in enumerate(table):
            address=tb+24*i;events.append(['read',address+4,identifier])
            if not identifier:return -1
            if identifier==wanted:
                events.extend([['write',base,i],['read',address+8,size],['write',base+4,size],['write',base+8,3],['write',base+12,address]])
                return i
        raise ValueError('unterminated oracle table')
    selected=scan(jedec)
    events.append(['read',base,selected&0xffffffff])
    if selected>=0:return 0,events
    scan(0xc22016)
    return 0xfffffffe,events


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'discover-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x161a4','--stop-address=0x16258',str(wrapper)],text=True))
    new=decode((out/'discover-linked.disassembly.txt').read_text());stock=IMAGE.read_bytes()
    shipped=[list(struct.unpack_from('<II',stock,0x18638+24*i+4)) for i in range(7)]
    tables=[shipped,[[0,0]],[[0xc22016,0xffffffff],[0,0]]]
    for slot in range(7):
        table=[row.copy() for row in shipped];table.insert(slot,[0xc22016,0x12345678]);tables.append(table)
    ids=[0,0xffffff,0xc22016,*[row[0] for row in shipped],*[(i*0x010101)&0xffffff for i in range(256)]]
    cases=0
    for table in tables:
        for jedec in ids:
            for transport in (0,1,0x7fffffff,0x80000000,0xffffffff):
                expected,events=oracle(jedec,transport,table)
                for seed in (0,0xffffffff):
                    if execute(old,0x161a4,0x1000dfec,jedec,transport,events,seed)!=expected or execute(new,0x10024190,0,jedec,transport,events,seed)!=expected:raise ValueError('discovery mismatch')
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'coverage':['Shipped table, empty table, fallback-only and fallback at every table position.', 'Positive/negative signed transport returns; JEDEC byte patterns; caller clobbers and complete 16-byte frame.', 'Ordered table reads and state writes; fallback still returns -2.'], 'limits':['Transport modeled; negative read returns are defensive-path checks, not behavior produced by the recovered polling transport.', 'Device table/state ownership and physical flash remain unqualified.']}
    (ROOT/'docs/research/gx8002-flash-discover-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
