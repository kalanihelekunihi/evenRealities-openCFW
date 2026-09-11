#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Formatter interpreter fork with an explicit decoded integer-helper boundary."""
import json
import re
import subprocess
from compare_gx8002_putchw import verify as verify_padding
from compare_gx8002_ui2a import signed
from compare_gx8002_uart_putc import register_list
from link_gx8002_uart_console import ROOT
from verify_gx8002_memcpy_source import decode


def execute(code, start, targets, fmt, arguments, fail_at=0, integer_hook=None, padding_hook=None, character_hook=None):
    r={f'r{i}':0x98760000+i for i in range(32)}
    r.update(r0=0x3000,r1=0x1000,r2=0x2000,r14=0x9000)
    initial=r.copy();memory={i:0xa5 for i in range(0x8e00,0x9000)}
    memory.update({0x1000+i:v for i,v in enumerate(fmt+b'\0')})
    def read(a,n):
        if any(a+i not in memory for i in range(n)):raise ValueError('outside memory')
        return sum(memory[a+i]<<(8*i) for i in range(n))
    def write(a,n,v):
        if any(a+i not in memory for i in range(n)):raise ValueError('outside write memory')
        for i in range(n):memory[a+i]=(v>>(8*i))&255
    def string(a):
        result=bytearray()
        for i in range(4096):
            v=read(a+i,1)
            if not v:return bytes(result)
            result.append(v)
        raise ValueError('unterminated string')
    for i,value in enumerate(arguments):
        if isinstance(value,bytes):
            a=0x4000+i*256
            memory.update({a+j:v for j,v in enumerate(value+b'\0')});value=a
        for j in range(4):memory[0x2000+i*4+j]=(value>>(8*j))&255
    pc,condition,saved,calls=start,False,None,bytearray()
    for _ in range(10000):
        op,args,length=code[pc];p=[v.strip() for v in args.split(',')];following=pc+length
        if op=='push':
            saved={x:r[x] for x in register_list(args)};r['r14']-=len(saved)*4
        elif op=='pop':
            if saved is None or set(saved)!=set(register_list(args)):raise ValueError('unbalanced save')
            r.update(saved);r['r14']+=len(saved)*4
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,12)) or r['r14']!=initial['r14']:raise ValueError('ABI restore failure')
            return r['r0'],bytes(calls)
        elif op in ('ld.b','ld.w','ldbi.b','ldbi.w','st.w','st.h','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+)(?:, (0x[0-9a-f]+))?\)',args)
            if not m:raise ValueError('unsupported memory operand')
            reg,ptr,off=m.groups();a=r[ptr]+int(off or '0',0);n=4 if op.endswith('.w') else 2 if op.endswith('.h') else 1
            if op.startswith('ld'):r[reg]=read(a,n)
            else:write(a,n,r[reg])
            if op.startswith('ldbi'):r[ptr]+=n
        elif op in ('mov','zextb'):r[p[0]]=r[p[1]]&(255 if op=='zextb' else 0xffffffff)
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op in ('addu','subu','addi','subi'):
            a=r[p[0] if len(p)==2 else p[1]];b=int(p[-1],0) if op in ('addi','subi') else r[p[-1]]
            r[p[0]]=(a-b if op in ('subu','subi') else a+b)&0xffffffff
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&0xffffffff
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='cmphsi':condition=r[p[0]]>=int(p[1],0)
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op=='cmplti':condition=signed(r[p[0]])<int(p[1],0)
        elif op=='mvcv':r[p[0]]=int(not condition)
        elif op in ('bt','bf','br','bez','bnez','bhsz'):
            take={'bt':condition,'bf':not condition,'br':True}.get(op)
            if take is None:take=r[p[0]]==0 if op=='bez' else r[p[0]]!=0 if op=='bnez' else signed(r[p[0]])>=0
            if take:following=int(p[-1],0)
        elif op=='bsr':
            kind=targets.get(int(p[0],0));parameter=r['r1'];result=0
            if kind=='integer':
                base=read(parameter+7,1);upper=read(parameter+8,1)
                text=format(r['r0'],{8:'o',10:'d',16:'x'}[base])
                if upper:text=text.upper()
                data=text.encode() if integer_hook is None else integer_hook(r['r0'],base,upper)
                if not isinstance(data,bytes) or b'\0' in data:raise ValueError('integer hook output')
                pointer=read(parameter+12,4)
                for i,v in enumerate(data+b'\0'):write(pointer+i,1,v)
            elif kind=='character':
                if r['r0']!=0x3000:raise ValueError('bad stream')
                calls.append(parameter&255);result=int(len(calls)!=fail_at)
                if character_hook is not None:result=character_hook(parameter&255,result)
            elif kind=='padding':
                if r['r0']!=0x3000:raise ValueError('bad stream')
                width=signed(read(parameter,4));lz=read(parameter+4,1);sign=read(parameter+5,1);alt=read(parameter+6,1);base=read(parameter+7,1);upper=read(parameter+8,1)
                text=string(read(parameter+12,4));prefix=bytes([sign]) if sign else b''
                if alt and base==16:prefix+=b'0X' if upper else b'0x'
                elif alt and base==8:prefix+=b'0'
                count=max(0,width-len(prefix)-len(text))
                if count>4096:raise ValueError('excessive width')
                emitted=(prefix+b'0'*count if lz else b' '*count+prefix)+text
                before=len(calls)
                if padding_hook is None:
                    result=len(emitted)-int(before<fail_at<=before+len(emitted))
                else:
                    result,emitted=padding_hook(width,lz,sign,alt,base,upper,text,fail_at-before if fail_at>before else 0)
                calls.extend(emitted)
            else:raise ValueError('unknown helper')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('instruction bound exceeded')

