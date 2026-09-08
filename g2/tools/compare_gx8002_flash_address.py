#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded address encoder with CK804 register-shift semantics."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_address import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,argument,events):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=0x20028000,r1=argument,r2=0x20028100);initial=r.copy();index=0;carry=None
    for _ in range(50):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('subi','andi','andni','and','or','addi','addu','subu','lsli','lsr'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op in ('subi','subu') else a+b if op in ('addi','addu') else a<<b if op=='lsli' else (a>>(b&63) if (b&63)<32 else 0) if op=='lsr' else a&~b if op=='andni' else a|b if op=='or' else a&b)&0xffffffff
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='bnezad':
            r[p[0]]=(r[p[0]]-1)&0xffffffff
            if r[p[0]]:n=int(p[1],0)
        elif op=='cmphsi':carry=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':carry=r[p[0]]>=r[p[1]]
        elif op in ('bt','br'):
            if op=='bt' and carry is None:raise ValueError('undefined comparison')
            if op=='br' or carry:n=int(p[-1],0)
        elif op in ('ld.w','st.b','stbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)\)',args) if op=='stbi.b' else re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown address')
            reg,base=m[1],m[2];address=r[base]+(0 if op=='stbi.b' else int(m[3],0))
            if index>=len(events):raise ValueError('extra access')
            e=events[index];index+=1
            if e[:2]!=['read' if op=='ld.w' else 'write',address] or op!='ld.w' and e[2]!=(r[reg]&255):raise ValueError('access mismatch')
            if op=='ld.w':r[reg]=e[2]
            if op=='stbi.b':r[base]+=1
        elif op=='rts':
            if index!=len(events) or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,18),*range(26,32))):raise ValueError('return state mismatch')
            return None
        else:raise ValueError('unknown OTP instruction '+op)
        pc=n
    raise ValueError('execution bound exceeded')

def oracle(address,widths):
    events=[]
    for i,width in enumerate(widths,1):
        # Each byte is selected from the low 3 bits of width-minus-position.
        byte_position=(width-i)%8
        value=(address//(256**byte_position))%256 if byte_position<4 else 0
        events.extend([['read',0x20028000,width],['write',0x20028100+i,value]])
    return events


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'address-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15ba0','--stop-address=0x15bec',str(wrapper)],text=True));new=decode((out/'address-linked.disassembly.txt').read_text());cases=0
    widths=[[w]*4 for w in (*range(16),0x7fffffff,0x80000000,0xffffffff)]+[[1,2,3,4],[4,3,2,1],[0,0xffffffff,8,0x80000000]]
    for byte in range(256):
        for position in range(4):
            address=(0x89abcdef&~(255<<(position*8)))|(byte<<(position*8))
            for schedule in widths:
                events=oracle(address,schedule)
                execute(old,0x15ba0,address,events);execute(new,0x10023b8c,address,events);cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,
            'architecture':'CK804 LSR takes low six count bits; counts 32..63 yield zero (ISA manual printed pages 243/244).',
            'coverage':['Every byte value in every address byte position; widths 0..15 and unsigned boundaries.', 'Changing width between the four reads; exact byte positions, access order and preserved registers.'],
            'limits':['Valid aligned width pointer and five-byte command buffer; no physical hardware qualification.']}
    (ROOT/'docs/research/gx8002-flash-address-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
