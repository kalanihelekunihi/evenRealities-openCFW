#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Execute format parsing with qualified helper semantics and bounded memory."""
import json
import re
import subprocess
from compare_gx8002_putchw import verify as verify_padding
from compare_gx8002_ui2a import signed
from compare_gx8002_uart_putc import register_list
from link_gx8002_uart_console import ROOT
from verify_gx8002_memcpy_source import decode


def execute(code, start, targets, fmt, arguments, fail_at=0):
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
                pointer=read(parameter+12,4)
                for i,v in enumerate(text.encode()+b'\0'):write(pointer+i,1,v)
            elif kind=='character':
                if r['r0']!=0x3000:raise ValueError('bad stream')
                calls.append(parameter&255);result=int(len(calls)!=fail_at)
            elif kind=='padding':
                if r['r0']!=0x3000:raise ValueError('bad stream')
                width=signed(read(parameter,4));lz=read(parameter+4,1);sign=read(parameter+5,1);alt=read(parameter+6,1);base=read(parameter+7,1);upper=read(parameter+8,1)
                text=string(read(parameter+12,4));prefix=bytes([sign]) if sign else b''
                if alt and base==16:prefix+=b'0X' if upper else b'0x'
                elif alt and base==8:prefix+=b'0'
                count=max(0,width-len(prefix)-len(text))
                if count>4096:raise ValueError('excessive width')
                emitted=(prefix+b'0'*count if lz else b' '*count+prefix)+text
                before=len(calls);calls.extend(emitted)
                result=len(emitted)-int(before<fail_at<=len(calls))
            else:raise ValueError('unknown helper')
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xdead0000+i
            r['r0']=result
        else:raise ValueError('unsupported instruction '+op)
        pc=following
    raise ValueError('instruction bound exceeded')


def verify():
    evidence=verify_padding();output=ROOT/'build/gx8002-tinyprintf';objdump=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'
    stock=decode(subprocess.check_output([str(objdump),'-D','--start-address=0x10010','--stop-address=0x101b0',str(output/'stock.elf')],text=True))
    source=decode(subprocess.check_output([str(objdump),'-d','--section=.text.tfp_format',str(output/'formatter.elf')],text=True))
    old={0xfeac:'integer',0xff24:'character',0xff3c:'padding'};new={a+0x101f6a74:k for a,k in old.items()}
    cases=[(b'',[],b''),(b'hello %%!',[],b'hello %!'),(b'end%',[],b'end'),(b'%q',[],b''),(b'%s %u',[b'abc',17],b'abc 17')]
    for spec in 'diuoxX':
      for value in (0,1,15,255,0x7fffffff,0x80000000,0xffffffff):
       for width in (0,1,8,16):
        for zeros in (False,True):
            fmt=('%'+('0' if zeros else '')+(str(width) if width else '')+spec).encode()
            number=signed(value) if spec in 'di' else value
            digits=format(abs(number),{'d':'d','i':'d','u':'d','o':'o','x':'x','X':'X'}[spec]);prefix='-' if number<0 else ''
            count=max(0,width-len(prefix)-len(digits));expected=(prefix+'0'*count if zeros else ' '*count+prefix)+digits
            cases.append((fmt,[value],expected.encode()))
    for spec,base in (('o',8),('x',16),('X',16)):
      for value in (0,1,255,0xffffffff):
       for width in (0,8,16):
        for zeros in (False,True):
            prefix='0' if base==8 else '0X' if spec=='X' else '0x'
            digits=format(value,spec)
            padding=max(0,width-len(prefix)-len(digits))
            expected=(prefix+'0'*padding if zeros else ' '*padding+prefix)+digits
            fmt=('%#'+('0' if zeros else '')+(str(width) if width else '')+spec).encode()
            cases.append((fmt,[value],expected.encode()))
    for value in (0,10,65,255,266,0xffffffff):
        cases.append((b'<%8c>',[value],b'<'+bytes([value&255])+b'>'))
    for text in (b'',b'a',b'abcdef'):
        cases.append((b'%8s',[text],b' '*max(0,8-len(text))+text))
        cases.append((b'%08s',[text],b'0'*max(0,8-len(text))+text))
    cases += [(b'%lu/%ld/%lx',[0xffffffff,0xffffffff,255],b'4294967295/-1/ff'),
              (b'%s:%x:%s:%d',[b'ab',255,b'cd',-12],b'ab:ff:cd:-12'),
              (b'%#',[],b''),(b'%0',[],b''),(b'%l',[],b''),
              (b'%q%u',[17],b'17')]
    comparisons=0
    for fmt,args,expected in cases:
      for fail in (0,1,3,9):
        a=execute(stock,0x10010,old,fmt,args,fail);b=execute(source,0x10206a84,new,fmt,args,fail)
        oracle=(len(expected)-int(0<fail<=len(expected)),expected)
        if a!=b or a!=oracle:raise ValueError(f'format mismatch {fmt} {args}: {a} {b}')
        comparisons+=1
    report={'helper_evidence':evidence,'format_cases':len(cases),'cases':comparisons,
            'source_admitted':False,'limits':['Helper semantics modeled; finite format corpus only.',
            'Variadic wrapper ABI remains unqualified; malformed widths and undefined inputs excluded.']}
    (ROOT/'docs/research/gx8002-format-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(comparisons);return report

if __name__=='__main__':verify()
