# SPDX-License-Identifier: MIT
"""Decoded DTO scaling slice; full clock function remains unqualified."""
import json,re,subprocess
from itertools import product
from link_gx8002_clock_frequency_candidate import ROOT,link
from verify_gx8002_memcpy_source import decode
from verify_gx8002_padmux_get import build as build_getter,programs
MASK=0xffffffff
PARAM=0x20031000
DTO=0x20031100
SP=0x2002f700
BASE=0xa0010000

def expected(present,word,frequency):
    trace=[(PARAM+12,4,DTO if present else 0)]
    if not present:return trace,frequency
    trace.extend([(DTO,1,0x24),(BASE+0x24,4,word)])
    return trace,frequency if word&(1<<27) else ((word&0x1ffffff)*frequency)>>25

def execute(code,entry,end,present,word,frequency):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=PARAM,r4=frequency,r14=SP)
    memory={(PARAM+12,4):DTO if present else 0,(DTO,1):0x24,(SP+4,4):BASE,(BASE+0x24,4):word};trace=[];pc=entry
    for _ in range(35):
        if pc==end:return trace,r['r4']
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('ld.w','ld.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('DTO load operand')
            reg,base,off=m.groups();a=(r[base]+int(off,0))&MASK;n=4 if op=='ld.w' else 1
            if (a,n) not in memory:raise ValueError('DTO read address')
            r[reg]=memory[a,n]
            if a!=SP+4:trace.append((a,n,r[reg]))
        elif op in ('bez','bnez'):
            if (r[p[0]]==0 if op=='bez' else r[p[0]]!=0):nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addu','and','or'):
            a,b=r[p[0]],r[p[1]];r[p[0]]=(a+b if op=='addu' else a&b if op=='and' else a|b)&MASK
        elif op in ('lsli','lsri'):
            r[p[0]]=(r[p[1]]<<int(p[2],0) if op=='lsli' else r[p[1]]>>int(p[2],0))&MASK
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op=='mul.u32':
            value=r[p[1]]*r[p[2]];r[p[0]]=value&MASK;r['r'+str(int(p[0][1:])+1)]=value>>32
        else:raise ValueError('Unhandled DTO instruction '+op)
        pc=nxt
    raise ValueError('DTO execution bound')

def verify():
    candidate=link();build_getter();programs();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x1732e','--stop-address=0x1738e',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-clock-frequency/frequency-analysis.disassembly.txt').read_text());count=0
    for args in product((False,True),(0,1,0x1ffffff,0x8000000,0x9ffffff,0xffffffff),(0,1,32000,24576000,98304000,MASK)):
        want=expected(*args)
        if execute(old,0x1732e,0x1738a,*args)!=want or execute(new,0x10025390,0x100252ac,*args)!=want:raise ValueError('DTO decoded mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,'limits':['DTO slice with valid descriptor and fixed entry state only; no whole-function ABI or hardware proof.']}
if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-dto-slice-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('Decoded DTO cases:',report['decoded_cases'])
