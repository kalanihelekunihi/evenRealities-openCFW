# SPDX-License-Identifier: MIT
"""Decoded selected-console port forwarding composed with UART port wrapper."""
import json,re,subprocess
from itertools import product
from compare_gx8002_format import ROOT,decode
from compare_gx8002_uart_putc import execute as uart


def execute(code,start,target,character,port,hook):
    r={f'r{i}':0x91370000+i for i in range(32)};r['r0']=character
    initial=r.copy();saved=None;pc=start;trace=[]
    for _ in range(20):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')]
        if op=='push':
            if args!='r15' or saved is not None:raise ValueError('Console frame')
            saved=r['r15']
        elif op=='pop':
            if args!='r15' or saved is None:raise ValueError('Console restore')
            r['r15']=saved
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Console ABI')
            return trace
        elif op=='lrw':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Console load operand')
            reg,base,off=m.groups();address=r[base]+int(off,0)
            if address!=0x2002731c:raise ValueError('Console port address')
            r[reg]=port;trace.append(('read',address,port))
        elif op=='bsr':
            if int(args,0)!=target:raise ValueError('Console UART target')
            trace.append(('uart',r['r0'],r['r1']));hook(r['r0'],r['r1'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xa9170000+i
        else:raise ValueError('Console instruction '+op)
        pc+=width
    raise ValueError('Console bound')


def programs():
    out=ROOT/'build/gx8002-uart-console';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    def old(start,end):return decode(subprocess.check_output([pre,'-D',f'--start-address={start:#x}',f'--stop-address={end:#x}',str(out/'stock.elf')],text=True))
    def new(symbol):return decode(subprocess.check_output([pre,'-d','--section=.text.open_cfw_gx8002_'+symbol,str(out/'console.elf')],text=True))
    return (old(0xcd7c,0xcd90),new('console_putc')),(old(0xcb40,0xcb64),new('uart_putc'))


def verify():
    consoles,uarts=programs();count=0
    for c,u,port,character in product((0,1),(0,1),(0,1,2),(0,10,13,255,256,0xffffffff)):
        transmitted=[]
        def hook(p,ch):transmitted.extend(uart(uarts[u],0x102035b4 if u else 0xcb40,0x1020324c if u else 0xc7d8,p,ch))
        trace=execute(consoles[c],0x102037f0 if c else 0xcd7c,0x102035b4 if c else 0xcb40,character,port,hook)
        want=[('read',0x2002731c,port),('uart',port,character)]
        descriptor=0x20026a94+(port<<7)
        expected=([(descriptor,13)] if character==10 else [])+[(descriptor,character&255)]
        if trace!=want or transmitted!=expected:raise ValueError('Console/UART composition')
        count+=1
    return {'decoded_cases':count,'source_admitted':False,'hardware_qualified':False,
            'limits':['Decoded console and UART port wrappers with separate register frames. Port global value and transmit calls modeled; no physical UART proof.']}


if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-console-boundary.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Console/UART cases:',report['decoded_cases'])
