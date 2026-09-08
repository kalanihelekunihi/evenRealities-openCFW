#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Replay decoded flash helpers against the qualified transport call contract."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_status import build, ROOT, IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code, pc, delta, statuses, seed=0):
    r={f'r{i}':0x45670000+i for i in range(32)}
    r['r14']=0x2002f7fc
    initial=r.copy(); stack={}; data={}; calls=[]; index=0
    for step in range(10000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];n=pc+width
        if op in ('push','pop'):
            if args!='r15':raise ValueError('unknown frame')
            if op=='push':
                r['r14']-=4
                if r['r14'] in stack:raise ValueError('frame overlap')
                stack[r['r14']]=r['r15']
            else:
                r['r15']=stack.pop(r['r14']);r['r14']+=4;n=r['r15']
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','andi'):
            a=r[p[0] if len(p)==2 else p[1]]
            b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a&b if op=='andi' else a+b)&0xffffffff
            if p[0]=='r14' and op=='subi':
                for address in range(r['r14'],r['r14']+b):data.pop(address,None)
        elif op=='ld.b':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unknown byte address')
            dst,base,off=m.groups();address=r[base]+int(off,0)
            if address not in data:raise ValueError('uninitialized status byte')
            r[dst]=data[address]
        elif op=='bnez':
            if r[p[0]]:n=int(p[1],0)
        elif op=='bsr':
            target=int(args,0);absolute=(target+delta)&0xffffffff
            r['r15']=n
            if absolute==0x10023734:n=target
            elif absolute in (0x10023684,0x100236dc):
                command,buffer,count=r['r0'],r['r1'],r['r2']
                if absolute==0x10023684:
                    if command not in (5,53) or count!=1 or buffer!=r['r14']+3 or buffer>=initial['r14'] or any(a <= buffer < a+4 for a in stack):raise ValueError('invalid status read contract')
                    if index==len(statuses):raise ValueError('status schedule exhausted')
                    value=statuses[index];index+=1;data[buffer]=value
                    calls.append(['read',command,buffer,count,value])
                else:
                    if (command,buffer,count)!=(6,0,0):raise ValueError('invalid write enable contract')
                    calls.append(['write',command,buffer,count])
                for i in (0,1,2,3,12,13):r[f'r{i}']=(0xa5a50000+seed*73+i)&0xffffffff
                r['r0']=0
            else:raise ValueError('unknown transport call')
        else:raise ValueError('unknown status instruction '+op)
        if n==initial['r15']:
            if stack or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('return state mismatch')
            if index!=len(statuses):raise ValueError('unconsumed status schedule')
            return r['r0'],calls
        pc=n
    raise ValueError('execution bound exceeded')


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    stock=out/'status-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(stock)],check=True)
    blob=bytearray(stock.read_bytes());struct.pack_into('<I',blob,36,0x21006009);stock.write_bytes(blob)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x15748','--stop-address=0x1579c',str(stock)],text=True))
    new=decode((out/'status-linked.disassembly.txt').read_text());cases=0
    for seed in (0,1,0xffff):
        for value in range(256):
            for entry,command in ((0x15748,5),(0x15784,53)):
                expected=(value,[['read',command,0x2002f7f7,1,value]])
                for code,delta in ((old,0x1000dfec),(new,0)):
                    if execute(code,entry+0x1000dfec-delta,delta,[value],seed)!=expected:raise ValueError('status result mismatch')
                cases+=1
        for ready in range(0,256,2):
            for busy in ([],[1],[255],[3,129,255,1]):
                schedule=busy+[ready]
                expected=(1,[['read',5,0x2002f7f3,1,v] for v in schedule])
                for code,delta in ((old,0x1000dfec),(new,0)):
                    if execute(code,0x1002375c-delta,delta,schedule,seed)!=expected:raise ValueError('ready loop mismatch')
                cases+=1
        for code,delta in ((old,0x1000dfec),(new,0)):
            if execute(code,0x1002374c-delta,delta,[],seed)!=(0,[['write',6,0,0]]):raise ValueError('write enable mismatch')
        cases+=1
    report={'build':evidence,'cases':cases,'transport_contract':'Source-qualified command read/write, successful completion; actual status-read helper is executed inside wait-ready.',
            'limits':['Finite status schedules; polling remains unbounded if busy never clears.', 'No physical flash qualification.']}
    (ROOT/'docs/research/gx8002-flash-status-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(cases);return report

if __name__=='__main__':verify()
