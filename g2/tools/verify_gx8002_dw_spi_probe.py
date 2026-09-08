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
from build_gx8002_dw_spi_probe_candidate import ROOT, build
from model_gx8002_dw_spi_probe import Case, expected
from verify_gx8002_memcpy_source import decode
import re

ADDRESS=0x10206480
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
        elif op=='incf':
            if not condition: r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('bez','bnez','bnezad'):
            if op=='bnezad': r[p[0]]=(r[p[0]]-1)&MASK
            if (r[p[0]]==0)==(op=='bez'): nxt=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or condition==(op=='bt'): nxt=int(args,0)
        elif op=='bsr':
            target=int(args,0)
            if target==0x10025080: event('clock',r['r0'],r['r1'])
            elif target==0x102060fc: event('register_master',r['r0'])
            elif target==0x1002553c: event('request_irq',r['r0'],r['r1'],r['r2'])
            else: raise ValueError('Unknown probe helper')
            for i in (0,1,2,3,12,13,15,*range(18,32)):
                r[f'r{i}']=(0xa7925693+i*0x113)&MASK
        else: raise ValueError('Unhandled probe instruction '+op)
        pc=nxt
    raise ValueError('Probe execution bound')


def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk)
    attribution=analyze()
    candidate=build()
    out=ROOT/'build/gx8002-board'
    stock=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(out/'dw-spi-full-oracle.elf')],text=True))
    source=decode((out/'dw-spi-probe-candidate.disassembly.txt').read_text())
    cases=[Case(a,b,c,d,s) for a,b,c,d,s in product((0,16,32),(0,16,32),(0,2,16,257),(0,2,16,257),((0,0),(8,9,0,1,0),(1,1,1,0)))]
    cases.extend(Case(tx_mismatch=n,rx_depth=16) for n in range(2,258))
    cases.extend(Case(rx_mismatch=n,tx_depth=16) for n in range(2,258))
    for case in cases:
        execute(stock,case)
        execute(source,case)
    if not candidate['fits']: raise ValueError('Probe exceeds slot')
    row={k:candidate[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':candidate['symbol'],'package_offset':0xfa0c,'bytes':268,
                               'sha256':candidate['stock_sha256'],'region':'image_a_xip_text'}]
    hashes={name:hashlib.sha256((ROOT/'tools'/name).read_bytes()).hexdigest()
            for name in ('verify_gx8002_dw_spi_probe.py','model_gx8002_dw_spi_probe.py',
                         'build_gx8002_dw_spi_probe_candidate.py','analyze_gx8002_dw_spi_probe.py')}
    if output:
        output.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(ROOT/'build/gx8002-board/dw-spi-probe-candidate.elf',output/'dw-spi-probe.elf')
    return {'functions':[row],'candidate':candidate,'attribution':attribution,'decoded_cases':len(cases),
            'evidence_sha256':hashes,'source_admitted':True,'hardware_qualified':False,
            'limits':['Fixed 12-byte frame and helper ABI modeled; helpers do not mutate state. Physical FIFO/clock behavior unqualified.']}

if __name__=='__main__':
    report=verify()
    (ROOT/'docs/research/gx8002-dw-spi-probe-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded probe cases:',report['decoded_cases'])
