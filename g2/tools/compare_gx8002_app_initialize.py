#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check startup call order and stack registration records against stock."""
import json
import re
import struct
import subprocess
from link_gx8002_app_initialize import link
from link_gx8002_uart_console import ROOT
from analyze_gx8002_upstream_objects import IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,start,delta,app,callback,returns,replace):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r14']=0x8000;initial=r.copy()
    memory={0x20026d38:app,0x20021004:callback};pc=start;saved=None;trace=[]
    for _ in range(80):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r15':raise ValueError('unexpected save')
            saved=r['r15']
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('unexpected restore')
            r['r15']=saved
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15)):raise ValueError('ABI mismatch')
            return r['r0'],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0);r[p[0]]=(a+b if op=='addi' else a-b)&0xffffffff
        elif op=='bez':
            if r[p[0]]==0:following=int(p[1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported memory operand')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='st.w':
                if address not in range(0x7ff0,0x8000,4):raise ValueError('unexpected stack write')
                memory[address]=r[reg]
            else:
                if address not in memory:raise ValueError('unmapped read')
                r[reg]=memory[address]
        elif op in ('bsr','jsr'):
            target=r[p[0]] if op=='jsr' else (int(p[0],0)+delta)&0xffffffff
            result=0
            if op=='jsr':
                if not callback or target!=callback:raise ValueError('unexpected callback')
                trace.append(('app_init',target));result=returns[0]
                if replace:memory[0x20026d38]=0
            elif target==0x10206f9c:trace.append(('queue',r['r0'],r['r1'],r['r2'],r['r3']))
            elif target in (0x102076c0,0x10207718):
                ptr=r['r0'];expected=0x7ff0 if target==0x102076c0 else 0x7ff8
                if ptr!=expected:raise ValueError('invalid record pointer')
                trace.append(('suspend' if target==0x102076c0 else 'resume',memory[ptr],memory[ptr+4]))
                result=returns[1 if target==0x102076c0 else 2]
            elif target==0x10206720:trace.append(('watchdog',r['r0'],r['r1'],r['r2'],r['r3']))
            else:raise ValueError('unexpected call')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    evidence=link();output=ROOT/'build/gx8002-app-tick';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=output/'startup-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x12260','--stop-address=0x122d4',str(wrapper)],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d',str(output/'app-initialize.elf')],text=True));cases=0
    for app,callback in ((0,0),(0x20021000,0),(0x20021000,0x10210000)):
        for result in (0,1,0xffffffff):
            for suspend in (0,0xffffffff):
                for resume in (0,0xffffffff):
                    for replace in (False,True):
                        expected=[('queue',0x2002ecd8,0x2002e880,64,8)]
                        if callback:expected.append(('app_init',callback))
                        expected += [('suspend',0x10208ca0,0x1020b3ee),('resume',0x10208c7c,0x1020b3fd),('watchdog',3000,2999,0x10208c98,0)]
                        oracle=(0,expected);returns=(result,suspend,resume)
                        if execute(old,0x12260,0x101f6a74,app,callback,returns,replace)!=oracle or execute(new,0x10208cd4,0,app,callback,returns,replace)!=oracle:raise ValueError('startup trace mismatch')
                        cases+=1
    report={'placement':evidence,'cases':cases,'source_admitted':False,'limits':['Returning AppInit callback and separately qualified service calls modeled.','No concurrent initialization, hardware startup or timing qualification.']}
    (ROOT/'docs/research/gx8002-app-initialize-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
