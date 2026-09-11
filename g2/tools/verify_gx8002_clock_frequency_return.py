# SPDX-License-Identifier: MIT
"""Frequency divider-call/return slice with explicit saved-frame state."""
import json
import subprocess
from itertools import product
from verify_gx8002_clock_size_probe import verify as build_probe, ROOT, decode
from verify_gx8002_padmux_get import build as build_getter, programs
MASK=0xffffffff
SP=0x2002f700
PARAM=0x20031000
BASE=0xa0010000


def execute(code, entry, delta, frequency, divider, divider_hook=None):
    initial={f'r{i}':(0x91234567+i*0x1020304)&MASK for i in range(32)}
    r=initial.copy();r.update(r0=PARAM,r4=frequency,r5=0,r14=SP)
    saved={SP+24:initial['r4'],SP+28:initial['r5'],SP+32:initial['r15']}
    pc=entry;calls=[]
    for _ in range(15):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='ld.w':
            if args!='r1, (r14, 0x4)' or r['r14']!=SP:raise ValueError('Return base load')
            r['r1']=BASE
        elif op=='bsr':
            if (int(args,0)+delta)&MASK!=0x10024ae8:raise ValueError('Return divider target')
            if (r['r0'],r['r1'])!=(PARAM,BASE):raise ValueError('Return divider arguments')
            calls.append((r['r0'],r['r1']))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xa5a50000+i
            r['r0']=divider if divider_hook is None else divider_hook(PARAM,BASE)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='divu':
            if not r[p[2]]:raise ValueError('Return zero division')
            r[p[0]]=r[p[1]]//r[p[2]]
        elif op=='br':nxt=int(args,0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='addi':r[p[0]]=(r[p[1]]+int(p[2],0))&MASK
        elif op=='pop':
            if args!='r4-r5, r15' or r['r14']!=SP+24:raise ValueError('Return frame')
            for index,reg in enumerate(('r4','r5','r15')):r[reg]=saved[r['r14']+index*4]
            r['r14']+=12
            if r['r14']!=SP+36 or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),15,16,17)):
                raise ValueError('Return callee registers')
            return calls,r['r0']
        else:raise ValueError('Unhandled return instruction '+op)
        pc=nxt
    raise ValueError('Return execution bound')


def verify():
    candidate=build_probe();build_getter();programs()
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x1737e','--stop-address=0x1739a',str(ROOT/'build/gx8002-board/padmux-get-stock.elf')],text=True))
    new=decode((ROOT/'build/gx8002-clock-frequency-size-probe/analysis.disassembly.txt').read_text())
    count=0
    for frequency,divider in product((0,1,32000,1024000,12288000,24576000,98304000,MASK),(0,1,2,3,32,65536,MASK)):
        want=([(PARAM,BASE)],frequency//divider if divider else frequency)
        for code,entry,delta in ((old,0x1738a,0x1000dfec),(new,0x100252a6,0)):
            if execute(code,entry,delta,frequency,divider)!=want:raise ValueError('Return slice mismatch')
        count+=1
    return {'candidate':candidate,'decoded_cases':count,'source_admitted':False,
            'limits':['Return slice assumes valid saved frame; divider result/caller clobbers modeled. Not full-function ABI or hardware proof.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-clock-frequency-return-verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Decoded return cases:',report['decoded_cases'])
