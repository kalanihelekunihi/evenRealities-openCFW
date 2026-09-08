#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute word callbacks against ordered effects and qualified polling contracts."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_word_io import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,command,buffer,count,events,delta):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=command,r1=buffer,r2=count,r14=0x2002f7fc)
    initial=r.copy();stack={};carry=None;index=0;steps=0
    def effect(kind,address,value=None):
        nonlocal index
        if index>=len(events):raise ValueError('unexpected extra effect')
        expected=events[index];index+=1
        if expected[:2]!=[kind,address] or value is not None and value!=expected[2]:raise ValueError('effect mismatch')
        return expected[2]
    while steps<2000000:
        steps+=1;op,args,width=code[pc];p=[v.strip() for v in args.split(',')];next_pc=pc+width
        if op in ('push','pop'):
            names={'r4-r6, r15':['r4','r5','r6','r15'],'r4, r15':['r4','r15']}.get(args)
            if names is None:raise ValueError('unsupported frame')
            if op=='push':
                r['r14']-=4*len(names)
                for i,n in enumerate(names):
                    a=r['r14']+i*4
                    if a in stack:raise ValueError('overlapping frame')
                    stack[a]=r[n]
            else:
                for i,n in enumerate(names):r[n]=stack.pop(r['r14']+i*4)
                r['r14']+=len(names)*4;next_pc=r['r15']
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('lsli','lsri','rotli','subi','andi','addu','addi','bseti'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else a>>b if op=='lsri' else a|(1<<b) if op=='bseti' else (a<<b)|(a>>(32-b)) if op=='rotli' else a-b if op=='subi' else a&b if op=='andi' else a+b)&0xffffffff
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported MMIO address')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w':r[reg]=effect('read',address)
            else:effect('write',address,r[reg])
        elif op in ('stbi.w','ldbi.w','ldr.w','str.w'):
            post=op in ('stbi.w','ldbi.w')
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args) if post else re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args)
            if not m:raise ValueError('unknown word buffer address')
            value,base=m[1],m[2];a=r[base]+(0 if post else r[m[3]]*4)
            if a%4 or not buffer<=a or a+4>buffer+(count//4)*4:raise ValueError('word buffer overrun')
            if op in ('stbi.w','str.w'):effect('buffer',a,r[value])
            else:r[value]=effect('buffer-read',a)
            if post:r[base]+=4
        elif op=='cmphsi':carry=r[p[0]]>=int(p[1],0)
        elif op=='cmpne':carry=r[p[0]]!=r[p[1]]
        elif op in ('bt','br','bez','bnez'):
            if op=='bt' and carry is None:raise ValueError('undefined comparison')
            if op=='br' or op=='bt' and carry or op in ('bez','bnez') and (r[p[0]]==0)==(op=='bez'):next_pc=int(p[-1],0)
        elif op=='bsr':
            target=int(args,0)+delta
            if target not in (0x1002364c,0x1002365c,0x10023670,0x1002375c):raise ValueError('unknown word I/O helper')
            effect('call',target,0)
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xa5a50000+i
            r['r0']=1 if target==0x1002375c else 0
        elif op=='rts':next_pc=r['r15']
        else:raise ValueError('unknown read instruction '+op)
        if next_pc==initial['r15']:
            if stack or index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('return state mismatch')
            return r['r0']
        pc=next_pc
    raise ValueError('read execution bound exceeded')

def oracle(program,address,buffer,length,jedec,delay):
    if not program and not length:return []
    words=length//4;events=[['call',0x1002364c,0]]
    def writes(rows):events.extend([['write',0xa2000000+off,value] for off,value in rows])
    if program:
        writes([(8,0),(0x10,0),(0x4c,0),(0,0x80041f),(4,(words-1)&0xffffffff),(0x10,1),(0x18,0x20000),(0xf4,0x40000218),(0x50,8),(0x4c,2),(8,1),(0x64,0x32),(0x64,address)])
    else:
        writes([(8,0),(0x4c,0),(0x10,0),(0,0x80081f),(4,(words-1)&0xffffffff),(0x18,0),(0x54,7)])
        events.append(['read',0x200264f0,0x20029000]);writes([(0x4c,1)])
        events.append(['read',0x20029004,jedec]);special=jedec in (0x1c3812,0x1c3813)
        writes([(0xf4,0x40003219 if special else 0x40004218),(8,1),(0x64,0xeb if special else 0x6b),(0x64,address),(0x10,1)])
    for i in range(words):
        events.extend([['read',0xa2000028,0]]*delay+[['read',0xa2000028,2 if program else 8]])
        word=(0x89abcdef+i*0x1020304)&0xffffffff
        if program:events.extend([['buffer-read',buffer+i*4,word],['write',0xa2000060,word]])
        else:events.extend([['read',0xa2000060,word],['buffer',buffer+i*4,word]])
    events.append(['call',0x10023670 if program else 0x1002365c,0])
    if program:events.append(['call',0x1002375c,0])
    writes([(8,0),(0x4c,0),(8,1)])
    return events


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'word-io-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x1579c','--stop-address=0x15d6c',str(w)],text=True))
    new=decode((out/'word-io-linked.disassembly.txt').read_text());cases=0
    for program in (False,True):
        for jedec in ((0,) if program else (0,0x1c3811,0x1c3812,0x1c3813,0x1c3814,0x854012,0x80000000,0xffffffff)):
            for length in (*range(66),255,256,257,1024):
                for address in (0,0xffffffff):
                    for delay in (0,2):
                        buffer=0 if length<4 else 0x20028000
                        events=oracle(program,address,buffer,length,jedec,delay)
                        entry=0x1579c if program else 0x15cc0
                        if execute(old,entry,address,buffer,length,events,0x1000dfec)!=0 or execute(new,entry+0x1000dfec,address,buffer,length,events,0)!=0:raise ValueError('word I/O result mismatch')
                        cases+=1
        events=oracle(program,0x800000,0x20030000,65536,0,1);entry=0x1579c if program else 0x15cc0
        for code,delta in ((old,0x1000dfec),(new,0)):
            if execute(code,entry+0x1000dfec-delta,0x800000,0x20030000,65536,events,delta)!=0:raise ValueError('large transfer mismatch')
        cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Qualified polling helpers modeled with caller clobbers; finite FIFO readiness schedules.', 'Aligned valid nonwrapping buffers. Every length 0..65, boundaries 255/256/257/1024, and a 64KiB transfer; larger domains and physical controller behavior remain unqualified.']}
    (ROOT/'docs/research/gx8002-flash-word-io-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
