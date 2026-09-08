#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute command reads and all nested polling helpers against ordered effects."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_transport import build,ROOT,IMAGE
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
    while steps<20000:
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
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('lsli','rotli','subi','andi','addu'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a<<b if op=='lsli' else (a<<b)|(a>>(32-b)) if op=='rotli' else a-b if op=='subi' else a&b if op=='andi' else a+b)&0xffffffff
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported MMIO address')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w':r[reg]=effect('read',address)
            else:effect('write',address,r[reg])
        elif op in ('stbi.b','ldbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args)
            if not m:raise ValueError('unsupported buffer store')
            value,base=m.groups();a=r[base]
            if not buffer<=a<buffer+count:raise ValueError('buffer overrun')
            if op=='stbi.b':effect('buffer',a,r[value]&255)
            else:r[value]=effect('buffer-read',a)
            r[base]=(a+1)&0xffffffff
        elif op=='cmpne':carry=r[p[0]]!=r[p[1]]
        elif op in ('bt','br','bez','bnez'):
            if op=='bt' and carry is None:raise ValueError('undefined comparison')
            if op=='br' or op=='bt' and carry or op in ('bez','bnez') and (r[p[0]]==0)==(op=='bez'):next_pc=int(p[-1],0)
        elif op=='bsr':
            target=int(args,0)
            if target+delta not in (0x1002364c,0x1002365c,0x10023670):raise ValueError('unknown polling helper')
            r['r15']=next_pc;next_pc=target
        elif op=='rts':next_pc=r['r15']
        else:raise ValueError('unknown read instruction '+op)
        if next_pc==initial['r15']:
            if stack or index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('return state mismatch')
            return r['r0']
        pc=next_pc
    raise ValueError('read execution bound exceeded')


def oracle(command,buffer,count,delay):
    status=0xa2000028
    events=[['read',status,1]]*delay+[['read',status,0]]
    events += [['write',0xa2000000+off,value] for off,value in [(8,0),(0x4c,0),(0,0xc07),(4,(count-1)&0xffffffff),(0x10,1),(0x18,0),(0xf4,0),(8,1),(0x60,command)]]
    for i in range(count):
        word=0xabcd0000|((i*71+255)&255)
        events += [['read',status,0]]*delay+[['read',status,8],['read',0xa2000060,word],['buffer',buffer+i,word&255]]
    events += [['read',0xa2000024,3]]*delay+[['read',0xa2000024,0]]
    events += [['read',status,1]]*delay+[['read',status,0]]
    return events


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'read-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15660','--stop-address=0x156f0',str(w)],text=True))
    new=decode((out/'transport-linked.disassembly.txt').read_text());cases=0
    for command in (0,5,21,255,0xffffffff):
        for count in range(257):
            for buffer in ((0,0x20028000,0x20028001) if count==0 else (0x20028000,0x20028001)):
                for delay in (0,1,3):
                    events=oracle(command,buffer,count,delay)
                    if execute(old,0x15698,command,buffer,count,events,0x1000dfec)!=0 or execute(new,0x10023684,command,buffer,count,events,0)!=0:raise ValueError('transport return mismatch')
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['All counts 0..256 with valid nonwrapping buffers; NULL only at count zero. Larger counts and other address domains remain unqualified.', 'Finite hardware readiness schedules; no hardware timing or liveness claim.']}
    (ROOT/'docs/research/gx8002-spi-read-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
