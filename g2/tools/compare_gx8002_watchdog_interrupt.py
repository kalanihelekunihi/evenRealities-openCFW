#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check watchdog ISR callback and interrupt-clear read order."""
import json
import re
import struct
import subprocess
from link_gx8002_watchdog_initialize import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,start,irq,private,handler,result,status):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=irq,r1=private)
    initial=r.copy();trace=[];pc=start;saved=None
    for _ in range(30):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r15':raise ValueError('unexpected save')
            saved=r['r15']
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('unexpected restore')
            r['r15']=saved
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),15)):raise ValueError('ABI mismatch')
            return r['r0'],trace
        elif op in ('lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported read operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a==0x20027b48:r[reg]=handler
            elif a==0xa0700014:r[reg]=status
            else:raise ValueError('unexpected read')
            trace.append(('read',a,r[reg]))
        elif op=='jsr':
            if r[p[0]]!=handler or not handler:raise ValueError('unexpected callback')
            trace.append(('callback',handler,r['r0'],r['r1']))
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        elif op in ('br','bez'):
            if op=='br' or r[p[0]]==0:following=int(p[-1],0)
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    evidence=link();output=ROOT/'build/gx8002-app-tick';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    row=evidence['sections'][0]
    if not row['byte_exact']:raise ValueError('ISR no longer byte-exact')
    wrapper=output/'watchdog-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0xfc90','--stop-address=0xfcac',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.open_cfw_gx8002_watchdog_interrupt',str(output/'watchdog-initialize.elf')],text=True))
    cases=0
    for irq in (0,11,31,0xffffffff):
        for private in (0,0x20020000,0xffffffff):
            for handler in (0,0x10208c98):
                for result in (0,1,0x80000000,0xffffffff):
                    for status in (0,1,0xffffffff):
                        trace=[('read',0x20027b48,handler)]
                        if handler:trace.append(('callback',handler,irq,private))
                        trace.append(('read',0xa0700014,status));expected=(result if handler else 0,trace)
                        if execute(old,0xfc90,irq,private,handler,result,status)!=expected or execute(new,0x10206704,irq,private,handler,result,status)!=expected:raise ValueError('ISR trace mismatch')
                        cases+=1
    report={'placement':evidence,'cases':cases,'source_admitted':False,'limits':['Callback is modeled as returning and clobbering caller-saved registers.','Nonreturning callbacks do not reach the clear read; no hardware/timing qualification.']}
    (ROOT/'docs/research/gx8002-watchdog-interrupt-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
