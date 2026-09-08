#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded watchdog setup with ordered MMIO/call oracles."""
import json
import re
import subprocess
from compare_gx8002_watchdog_interrupt import verify as interrupt
from link_gx8002_uart_console import ROOT
from verify_gx8002_memcpy_source import decode


def execute(code,start,reset,level,handler,private,control,delta):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=reset,r1=level,r2=handler,r3=private)
    initial=r.copy();pc=start;condition=False;saved=None;trace=[]
    for _ in range(250):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];following=pc+width
        if op=='push':
            if args!='r4-r6, r15':raise ValueError('unexpected save')
            saved={k:r[k] for k in ('r4','r5','r6','r15')}
        elif op=='pop':
            if args!='r4-r6, r15' or saved is None:raise ValueError('unexpected restore')
            r.update(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),15)):raise ValueError('ABI mismatch')
            return trace
        elif op in ('movi','lrw','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','addu','lsli','lsl','ori','or','rotli','divu','divs'):
            a=r[p[0] if len(p)==2 else p[1]];b=r[p[-1]] if p[-1].startswith('r') else int(p[-1],0)
            if op in ('lsli','lsl','rotli') and b>=32:raise ValueError('invalid shift')
            if op=='divs':
                a=a-(1<<32) if a&0x80000000 else a;b=b-(1<<32) if b&0x80000000 else b
                v=(abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1)
            else:v=a+b if op in ('addi','addu') else a<<b if op in ('lsli','lsl') else a|b if op in ('ori','or') else (a<<b)|(a>>(32-b)) if op=='rotli' else a//b
            r[p[0]]=v&0xffffffff
        elif op in ('cmphsi','cmphs','cmpnei'):
            a=r[p[0]];b=r[p[1]] if p[1].startswith('r') else int(p[1],0);condition=a!=b if op=='cmpnei' else a>=b
        elif op in ('br','bt','bf','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&0xffffffff
            if {'br':True,'bt':condition,'bf':not condition}.get(op,r[p[0]]!=0 if op=='bnezad' else False):following=int(p[-1],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported memory operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='ld.w':
                if a!=0xa0700000:raise ValueError('unexpected read')
                r[reg]=control;trace.append(('read',a,control))
            else:
                if a not in (0xa0700000,0xa0700004,0xa070000c,0x20027b48):raise ValueError('unexpected write')
                trace.append(('write',a,r[reg]))
        elif op=='bsr':
            target=(int(p[0],0)+delta)&0xffffffff
            if target==0x10206c24:
                if r['r0']!=0x1020ad1a:raise ValueError('wrong diagnostic')
                trace.append(('printf',r['r0']))
            elif target==0x10025080:trace.append(('gate',r['r0'],r['r1']))
            elif target==0x1002553c:trace.append(('irq',r['r0'],r['r1'],r['r2']))
            else:raise ValueError('unexpected call')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('execution bound exceeded')


def verify():
    evidence=interrupt();output=ROOT/'build/gx8002-app-tick';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0xfcac','--stop-address=0xfd2c',str(output/'watchdog-stock.elf')],text=True))
    new=decode(subprocess.check_output([str(prefix)+'objdump','-d','--section=.text.open_cfw_gx8002_watchdog_initialize',str(output/'watchdog-initialize.elf')],text=True))
    cases=0
    corpus=[(level,0,0x10208c98,0x20020000,0xa5a5a5a4) for level in range(65536)]
    corpus += [(level,reset,handler,private,control) for level in (0,999,1000,1999,2000,2999,3000,65535) for reset in (0,65535) for handler in (0,0x10208c98) for private in (0,0xffffffff) for control in (0,1,0xffffffff)]
    for level,reset,handler,private,control in corpus:
        if level<1000:expected=[('printf',0x1020ad1a)]
        else:
            setting=next(i for i in range(16) if (1<<(i+16))//1000000>=level//1000)
            expected=[('gate',24,1),('write',0xa0700004,setting*17),('write',0xa070000c,118),('write',0x20027b48,handler),('irq',11,0x10206704,private),('read',0xa0700000,control),('write',0xa0700000,control|1)]
        if execute(old,0xfcac,reset,level,handler,private,control,0x101f6a74)!=expected or execute(new,0x10206720,reset,level,handler,private,control,0)!=expected:raise ValueError('watchdog setup mismatch')
        cases+=1
    report={'interrupt_evidence':evidence,'cases':cases,'source_admitted':False,'limits':['Gate, IRQ registration and printf calls modeled; each separately qualified.','C uint16_t ABI inputs only; no hardware timing or asynchronous interrupt simulation.']}
    (ROOT/'docs/research/gx8002-watchdog-initialize-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report

if __name__=='__main__':verify()
