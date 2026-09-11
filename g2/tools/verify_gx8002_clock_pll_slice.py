# SPDX-License-Identifier: MIT
"""Decoded PLL arithmetic slice; not whole-frequency admission."""
import json,re,subprocess
from itertools import product
from link_gx8002_clock_frequency_candidate import ROOT,link
from verify_gx8002_memcpy_source import decode
from verify_gx8002_padmux_get import build as build_getter,programs
from model_gx8002_clock_pll_frequency import frequency
MASK=0xffffffff

def execute(code,entry,ends,words,table=None):
    r={f'r{i}':0 for i in range(32)};pc=entry;condition=False;reads=[]
    memory=dict(zip((0xa000501c,0xa0005020,0xa0005024,0xa0005028,0xa0005030),words))
    for _ in range(100):
        if pc in ends:return reads,r['r4']
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('lrw','movi','movih'):r[p[0]]=(int(p[1],0)<<(16 if op=='movih' else 0))&MASK
        elif op=='ldr.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << 2\)',args)
            if not m or table is None:raise ValueError('PLL table operand')
            reg,base,index=m.groups();address=r[base]+4*r[index]
            if address not in table:raise ValueError('PLL table address')
            r[reg]=table[address]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('PLL load operand')
            reg,base,off=m.groups();a=(r[base]+int(off,0))&MASK
            if a not in memory:raise ValueError('PLL read address')
            r[reg]=memory[a];reads.append((a,r[reg]))
        elif op in ('addi','subi','andi','lsli','rotli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];b=int(p[-1],0)
            r[p[0]]=(a+b if op=='addi' else a-b if op=='subi' else a&b if op=='andi' else a<<b if op=='lsli' else (a<<b)|(a>>(32-b)))&MASK
        elif op in ('addu','and','or','nor','mult','divu'):
            a,b=(r[p[1]],r[p[2]]) if len(p)==3 else (r[p[0]],r[p[1]])
            if op=='divu' and not b:raise ValueError('PLL zero divisor')
            r[p[0]]=(a+b if op=='addu' else a&b if op=='and' else a|b if op=='or' else ~(a|b) if op=='nor' else a*b if op=='mult' else a//b)&MASK
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('cmpnei','cmphsi','cmphs'):
            a=r[p[0]];b=r[p[1]] if op=='cmphs' else int(p[1],0)
            condition=a!=b if op=='cmpnei' else a>=b
        elif op=='inct':
            if condition:r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op in ('bt','bf','br'):
            if op=='br' or (condition if op=='bt' else not condition):nxt=int(args,0)
        else:raise ValueError('Unhandled PLL instruction '+op)
        pc=nxt
    raise ValueError('PLL execution bound')

def verify():
    candidate=link();build_getter();programs();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x17224','--stop-address=0x173e0',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-clock-frequency/frequency-analysis.disassembly.txt').read_text());count=0
    for words in product((0,1,31,63),(0,59,95,255,2047),(0,1,31),(0,7),(0,16,32,48)):
        wanted=frequency(*words)
        for code,entry,ends in ((old,0x172b0,(0x1732e,0x1737e)),(new,0x100252f2,(0x10025390,0x10025246))):
            reads,result=execute(code,entry,ends,words)
            if result!=wanted or [a for a,v in reads]!=[0xa000501c,0xa0005020,0xa0005024,0xa0005028,0xa0005030]:raise ValueError('PLL decoded mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'limits':['PLL slice only; fixed entry/exit states, no full-function ABI, DTO/divider composition or hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-pll-slice-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Decoded PLL cases:',report['decoded_cases'])
