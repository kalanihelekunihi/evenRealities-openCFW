#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare IRQ dispatch body traces, independently of interrupt frames."""
import json
import re
import struct
import subprocess
from build_gx8002_irq_entry_candidate import build
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,start,status,handler,private,stop=None):
    r={f'r{i}':0x98760000+i for i in range(32)};initial=r.copy();pc=start;saved=None;trace=[]
    irq=(status&511)-32
    if not 0<=irq<32:raise ValueError('outside qualified IRQ domain')
    for _ in range(40):
        if pc==stop:return trace
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r15':raise ValueError('unexpected save')
            saved=r['r15']
        elif op in ('pop','rts'):
            if op=='pop':
                if args!='r15' or saved is None:raise ValueError('unexpected restore')
                r['r15']=saved
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),15)):raise ValueError('ABI mismatch')
            return trace
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op in ('andi','subi','addu','lsli'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a&b if op=='andi' else a-b if op=='subi' else a+b if op=='addu' else a<<b)&0xffffffff
        elif op=='bez':
            if r[p[0]]==0:following=int(p[1],0)
        elif op in ('ld.w','ldr.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << 3)\)',args)
            if not m:raise ValueError('unsupported memory operand')
            reg,base,off=m.groups();address=r[base]+(r[off.split()[0]]<<3 if '<<' in off else int(off,0))
            values={0xe000ec00:status,0x20026ef4+irq*8:handler,0x20026ef8+irq*8:private}
            if address not in values:raise ValueError('unexpected read')
            r[reg]=values[address];trace.append(('read',address,r[reg]))
        elif op=='jsr':
            if not handler or r[p[0]]!=handler:raise ValueError('unexpected handler')
            trace.append(('handler',handler,r['r0'],r['r1']))
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    evidence=build();output=ROOT/'build/gx8002-irq';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=output/'dispatch-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x1759a','--stop-address=0x175b8',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d',str(output/'entry.elf')],text=True));cases=0
    for irq in range(32):
        for upper in (0,0x200,0x80000000,0xfffffe00):
            status=upper|(irq+32)
            for handler in (0,0x10206704):
                for private in (0,0x20020000,0xffffffff):
                    expected=[('read',0xe000ec00,status),('read',0x20026ef4+irq*8,handler)]
                    if handler:expected += [('read',0x20026ef8+irq*8,private),('handler',handler,irq,private)]
                    if execute(old,0x1759a,status,handler,private,0x175b8)!=expected or execute(new,0x10025598,status,handler,private)!=expected:raise ValueError('dispatch trace mismatch')
                    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Stock body is sliced before frame restoration; frame behavior qualified separately.','Valid IRQ vectors 32..63 only; no invalid-vector or actual nested interrupt qualification.','Handler calls modeled with ABI caller-saved clobbers.']}
    (ROOT/'docs/research/gx8002-irq-dispatch-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
