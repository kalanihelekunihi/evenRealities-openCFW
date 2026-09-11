# SPDX-License-Identifier: MIT
"""Decode lookup-result gate; no whole-function or lookup-body proof."""
import json
import re
import subprocess
from itertools import product
from analyze_gx8002_clock_table_placement import analyze,ROOT
from verify_gx8002_padmux_get import build as build_getter,programs
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
SP=0x2002f700
PARAM=0x20031000


def execute(code,source,result,byte):
    r={f'r{i}':0x12340000+i for i in range(32)};r.update(r0=result,r14=SP)
    pc=0x10025232 if source else 0x17246
    stop=0x10025258 if source else 0x1725a
    ret=0x10025246 if source else 0x1737e
    trace=[];condition=False
    for _ in range(15):
        if pc==stop:return trace,'selection',r['r2' if source else 'r1']
        if pc==ret:return trace,'return',r['r4']
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op in ('ld.w','ld.bs'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Lookup-result load operand')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if op=='ld.w' and address==SP:r[reg]=PARAM
            elif op=='ld.bs' and address==PARAM+6:
                r[reg]=(byte if byte<128 else byte-256)&MASK;trace.append((address,1,byte))
            else:raise ValueError('Lookup-result read address')
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='bnez':
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        else:raise ValueError('Unhandled lookup-result instruction '+op)
        pc=nxt
    raise ValueError('Lookup-result bound')


def verify():
    candidate=analyze();build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x17246','--stop-address=0x173c0',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-clock-frequency-table-probe/placement.disassembly.txt').read_text());count=0
    for result,byte in product((0,1,2,0x80000000,MASK),range(256)):
        want=([],'return',0) if result else ([(PARAM+6,1,byte)],'return',0) if byte==255 else ([(PARAM+6,1,byte)],'selection',(byte if byte<128 else byte-256)&MASK)
        if execute(old,False,result,byte)!=want or execute(new,True,result,byte)!=want:raise ValueError('Lookup-result mismatch')
        count+=1
    return {'placement':candidate,'decoded_cases':count,'source_admitted':False,
            'limits':['Lookup result modeled; all signed-byte outcomes checked only through gate. Negative offsets other than -1 are not qualified for subsequent shifts.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-lookup-result.json').write_text(json.dumps(report,indent=2)+'\n');print('Lookup-result cases:',report['decoded_cases'])
