#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Replay decoded probe accesses against the independent transaction model."""
import json
import hashlib
import shutil
from verify_gx8002_logging import check_paths
import subprocess
from itertools import product
from analyze_gx8002_dw_spi_probe import analyze
from build_gx8002_backup_dw_spi_probe import ROOT, build, IMAGE, IMAGE_SHA, sha, Elf32
from model_gx8002_backup_dw_spi_probe import Case, expected
from verify_gx8002_memcpy_source import decode
import re

ADDRESS=0x100085ac
MASK=0xffffffff


def execute(code,case):
    wanted,depths=expected(case)
    events=iter(wanted)
    def event(kind,*args):
        try: item=next(events)
        except StopIteration: raise ValueError('Extra probe transaction')
        if item[:len(args)+1]!=(kind,*args):
            raise ValueError('Probe transaction mismatch: '+repr((kind,args,item)))
        return item[-1]
    r={f'r{i}':(0x97123568+i*0x1020304)&MASK for i in range(32)}
    r['r14']=0x2002f7fc
    initial=r.copy()
    saved=None
    condition=False
    pc=ADDRESS
    for _ in range(12000):
        op,args,width=code[pc]
        p=[x.strip() for x in args.split(',')]
        nxt=pc+width
        if op=='push':
            if args!='r4-r5, r15' or saved is not None: raise ValueError('Probe frame')
            saved=[r[x] for x in ('r4','r5','r15')]
            r['r14']-=12
        elif op=='pop':
            if args!='r4-r5, r15' or saved is None: raise ValueError('Probe return')
            for reg,value in zip(('r4','r5','r15'),saved): r[reg]=value
            r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):
                raise ValueError('Probe ABI')
            if next(events,None) is not None: raise ValueError('Missing probe transaction')
            return depths
        elif op in ('movi','lrw','movih'):
            r[p[0]]=(int(p[1],0)<<(16 if op=='movih' else 0))&MASK
        elif op=='mov': r[p[0]]=r[p[1]]
        elif op in ('addi','subi','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]]
            b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a<<b)&MASK
        elif op=='bseti': r[p[0]]|=1<<int(p[1],0)
        elif op=='andi': r[p[0]]=r[p[1]]&int(p[2],0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match: raise ValueError('Probe memory operand')
            reg,base,off=match.groups()
            address=(r[base]+int(off,0))&MASK
            if op=='ld.w': r[reg]=event('read',address)
            else: event('write',address,r[reg])
        elif op in ('cmpne','cmpnei'):
            condition=r[p[0]]!=(r[p[1]] if op=='cmpne' else int(p[1],0))
        elif op=='inct':
            if condition: r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='incf':
            if not condition: r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad': r[p[0]]=(r[p[0]]-1)&MASK
            if (r[p[0]]==0)==(op=='bez'): nxt=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'): nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0)
            if target==0x10003be8: event('clock',r['r0'],r['r1'])
            elif target==0x10008218: event('register_master',r['r0'])
            elif target==0x10004844: event('request_irq',r['r0'],r['r1'],r['r2'])
            else: raise ValueError('Unknown probe helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):
                r[f'r{i}']=(0xa7925693+i*0x113)&MASK
        else: raise ValueError('Unhandled probe instruction '+op)
        pc=nxt
    raise ValueError('Probe execution bound')


def verify():
    candidate=build();assert candidate['fits']
    path=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(path.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    raw=decode(subprocess.check_output([pre,'-D','--start-address=0x40eec','--stop-address=0x4101c',str(path)],text=True));stock={};delta=0x10000000-0x38940
    for pc,(op,args,width) in raw.items():
        if op in ('bsr','br','bt','bf','bez','bnez','bnezad'):
            parts=args.split(',');parts[-1]=hex(int(parts[-1].strip(),0)+delta);args=','.join(parts)
        stock[pc+delta]=(op,args,width)
    source=decode((ROOT/'build/gx8002-backup-dw-spi-probe/dw-spi-probe-candidate.disassembly.txt').read_text())
    cases=[Case(a,b,c,d,s) for a,b,c,d,s in product((0,16,32),(0,16,32),(0,2,16,257),(0,2,16,257),((0,0),(8,9,0,1,0),(1,1,1,0)))]
    cases.extend(Case(tx_mismatch=n,rx_depth=16) for n in range(2,258))
    cases.extend(Case(rx_mismatch=n,tx_depth=16) for n in range(2,258))
    for case in cases:
        execute(stock,case);execute(source,case)
    report={'candidate':candidate,'decoded_cases':len(cases),'source_admitted':False,'limits':['Helpers modeled without state mutations; controller pointer reloads checked in ordered transaction trace.','All mismatch positions and no-mismatch detection checked; physical clock/FIFO behavior and linked callback implementations remain unqualified.']}
    (ROOT/'docs/research/gx8002-backup-dw-spi-probe-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['decoded_cases'])
