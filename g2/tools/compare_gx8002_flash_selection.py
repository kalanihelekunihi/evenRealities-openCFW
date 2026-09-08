#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare decoded flash-ID dispatch, including state changes by callees."""
import contextlib
import io
import json
import re
import struct
import subprocess
from build_gx8002_flash_candidate import build, ROOT, IMAGE
from verify_gx8002_memcpy_source import decode


def execute(code,pc,stop,first,second,delta=0):
    r={f'r{i}':0x12340000+i for i in range(32)};r['r5']=1
    trace=[];carry=None;loads=0
    for _ in range(70):
        if pc==stop:return trace
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')];following=pc+width
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('unsupported state read')
            dst,base,offset=m.groups();address=r[base]+int(offset,0)
            if address==0x200264f0:
                loads+=1
                if loads>2:raise ValueError('unexpected pointer reload')
                value=0x20028000 if loads==1 else 0x20029000
            elif address==0x20028004 and loads==1:value=first
            elif address==0x20029004 and loads==2:value=second
            else:raise ValueError('unknown state read')
            r[dst]=value;trace.append(['read',address,value])
        elif op in ('cmpne','cmplt','cmphs','cmphsi'):
            a=r[p[0]];b=int(p[1],0) if op=='cmphsi' else r[p[1]]
            if op=='cmplt':a=a-(1<<32) if a&0x80000000 else a;b=b-(1<<32) if b&0x80000000 else b
            carry=a!=b if op=='cmpne' else a<b if op=='cmplt' else a>=b
        elif op in ('br','bt','bf'):
            if op!='br' and carry is None:raise ValueError('undefined condition')
            if op=='br' or carry==(op=='bt'):following=int(args,0)
        elif op=='bsr':
            target=int(p[0],0)+delta
            if target not in (0x100242b4,0x10024330,0x100242ec):raise ValueError('unexpected flash service')
            trace.append(['call',target])
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=0xfedc0000+i
        else:raise ValueError('unsupported selection instruction '+op)
        pc=following
    raise ValueError('selection bound exceeded')


def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';prefix=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'selection-stock.elf'
    subprocess.run([str(prefix)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    data=bytearray(wrapper.read_bytes());struct.pack_into('<I',data,36,0x21006009);wrapper.write_bytes(data)
    old=decode(subprocess.check_output([str(prefix)+'objdump','-D','--start-address=0x16654','--stop-address=0x1668e',str(wrapper)],text=True))
    new=decode((out/'flash.disassembly.txt').read_text())
    ids={0,0xffffffff,0x80000000,0x7fffffff}
    for value in (0x1c3812,0x1c3813,0x854012,0x856013,0x856014,0x204016):
        ids.update((value-1,value,value+1))
    ids.update((i*0x9e3779b9)&0xffffffff for i in range(256))
    cases=0
    for first in sorted(ids):
        for second in (0,0x204016,0xffffffff):
            expected=[['read',0x200264f0,0x20028000],['read',0x20028004,first]]
            if first in (0x854012,0x856013):expected.append(['call',0x10024330])
            elif first not in (0x1c3812,0x1c3813):expected.append(['call',0x100242b4])
            expected += [['read',0x200264f0,0x20029000],['read',0x20029004,second]]
            if second==0x204016:expected.append(['call',0x100242ec])
            if execute(old,0x16654,0x1668e,first,second,0x1000dfec)!=expected or execute(new,0x1002463e,0x10024666,first,second)!=expected:raise ValueError('flash selection mismatch')
            cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':[
        'Only successful-discovery device selection is modeled; setup, failure return, callbacks and XIP arguments remain separate.',
        'Models changed state pointers/IDs between reads and ABI-clobbering returning services; no hardware behavior claim.',
        'Candidate r5=1 is supplied from the preceding decoded setup and needs full-routine verification.']}
    (ROOT/'docs/research/gx8002-flash-selection-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report


if __name__=='__main__':verify()
