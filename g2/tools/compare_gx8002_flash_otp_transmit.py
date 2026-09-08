#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute word callbacks against ordered effects and qualified polling contracts."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_otp_transmit import build,ROOT,IMAGE
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
            names={'r4-r6, r15':['r4','r5','r6','r15']}.get(args)
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
        elif op in ('ld.b','ldbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args) if op=='ld.b' else re.fullmatch(r'(r\d+), \((r\d+)\)',args)
            if not m:raise ValueError('unknown byte address')
            reg,base=m[1],m[2];address=(r[base]+(int(m[3],0) if op=='ld.b' else 0))&0xffffffff
            r[reg]=effect('byte-read',address)&255
            if op=='ldbi.b':r[base]=(r[base]+1)&0xffffffff
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
            if r['r14']!=initial['r14']-16:raise ValueError('frame mismatch')
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

def oracle(prefix,buffer,length,delay):
    events=[['call',0x1002364c,0]]
    def write(address,value):events.append(['write',address,value])
    write(0xa2000008,0);write(0xa0300090,2)
    for offset,value in ((0x4c,0),(0x10,0),(0,0x407),(4,(length-1)&0xffffffff),(0x18,0),(0xf4,0),(0x50,8),(8,1)):
        write(0xa2000000+offset,value)
    for phase,count in ((0,prefix),(1,length)):
        if phase:write(0xa2000010,1)
        for i in range(count):
            events.extend([['read',0xa2000028,0]]*delay+[['read',0xa2000028,2]])
            value=(i*73+phase*19+0x81)&255
            address=((0x200264f4 if not phase else buffer)+i)&0xffffffff
            events.append(['byte-read',address,value]);write(0xa2000060,value)
    events.append(['call',0x10023670,0])
    write(0xa2000008,0);write(0xa0300090,3);write(0xa0300090,1);write(0xa2000008,1)
    events.append(['call',0x1002375c,0])
    return events

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';w=out/'otp-transmit-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15e28','--stop-address=0x15ecc',str(w)],text=True))
    new=decode((out/'otp-transmit-linked.disassembly.txt').read_text());cases=0
    for prefix in range(9):
     for length in (*range(34),255,256,257,1024):
      for buffer in (0x20028000,0xfffffffe):
       for delay in (0,2):
        events=oracle(prefix,buffer,length,delay)
        for code,entry,delta in ((old,0x15e28,0x1000dfec),(new,0x10023e14,0)):
            if execute(code,entry,prefix,buffer,length,events,delta)!=0:raise ValueError('transmit result')
        cases+=1
    report={'frame_bytes':16,'build':evidence,'cases':cases,'source_admitted':False,
            'limits':['Modeled helper clobbers and finite FIFO readiness. Synthetic wrapped pointers do not certify physical buffer validity. Rejection tests and admission remain.']}
    (ROOT/'docs/research/gx8002-flash-otp-transmit-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(cases);return report
if __name__=='__main__':verify()
