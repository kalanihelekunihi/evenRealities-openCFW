#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare padding target paths with modeled putf calls and output oracle."""
import json
import re
import subprocess
from compare_gx8002_ui2a import verify as verify_integer, signed
from compare_gx8002_uart_putc import register_list
from link_gx8002_uart_console import ROOT
from verify_gx8002_memcpy_source import decode


def execute(code, start, target, width, lz, sign, alt, base, upper, text, fail, character_hook=None):
    r = {f'r{i}': 0x98760000+i for i in range(32)}
    r.update(r0=0x3000, r1=0x1000)
    initial = r.copy()
    memory = {0x1000+i: 0 for i in range(16)}
    for i in range(4): memory[0x1000+i] = (width >> (8*i)) & 255
    for i,v in enumerate((lz,sign,alt,base,upper)): memory[0x1004+i] = v
    memory[0x100d] = 0x20
    memory.update({0x2000+i:v for i,v in enumerate(text+b'\0')})
    pc, condition, saved, calls = start, False, None, []
    for _ in range(10000):
        op,args,length=code[pc];p=[v.strip() for v in args.split(',')];following=pc+length
        if op == 'push': saved={x:r[x] for x in register_list(args)}
        elif op == 'pop':
            if saved is None or set(saved)!=set(register_list(args)): raise ValueError('unbalanced save')
            r.update(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,12)): raise ValueError('callee saved changed')
            return r['r0'],bytes(calls)
        elif op in ('ld.b','ld.w','ldbi.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args)
            if not m: raise ValueError('unsupported memory operand')
            reg,ptr,off=m.groups();a=r[ptr]+int(off or '0',0);n=4 if op=='ld.w' else 1
            if any(a+i not in memory for i in range(n)): raise ValueError('outside memory')
            r[reg]=sum(memory[a+i]<<(8*i) for i in range(n))
            if op=='ldbi.b': r[ptr]+=1
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addu','subu','addi','subi','max.s32'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op in ('addi','subi') else r[p[-1]]
            v=max(signed(a),signed(b)) if op=='max.s32' else a-b if op in ('subu','subi') else a+b
            r[p[0]]=v&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('dect','decf','incf'):
            if (condition if op=='dect' else not condition):
                r[p[0]]=(r[p[1]]+(-1 if op.startswith('dec') else 1)*int(p[2],0))&0xffffffff
        elif op in ('bt','bf','br','bez','bnez','bhz','blsz'):
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:
                v=r[p[0]];take=v==0 if op=='bez' else v!=0 if op=='bnez' else signed(v)>0 if op=='bhz' else signed(v)<=0
            if take:following=int(p[-1],0)
        elif op=='bsr':
            if int(p[0],0)!=target or r['r0']!=0x3000:raise ValueError('unexpected output call')
            character=r['r1']&255
            calls.append(character)
            result=int(len(calls)!=fail) if character_hook is None else character_hook(character,int(len(calls)!=fail))
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('instruction bound exceeded')

