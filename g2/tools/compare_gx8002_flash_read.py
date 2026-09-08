#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded read wrapper, with changing callback pointers and ABI clobbers."""
import contextlib,io,json,re,struct,subprocess
from build_gx8002_flash_read import build,ROOT,IMAGE
from verify_gx8002_memcpy_source import decode

def execute(code,pc,delta,address,destination,length,seed):
    r={f'r{i}':(seed+i*0x10203)&0xffffffff for i in range(32)};r.update(r0=address,r1=destination,r2=length,r14=0x2002f7fc)
    initial=r.copy();saved=None;trace=[];calls=0;reads=0
    for _ in range(500000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op=='push':
            if args!='r4-r9, r15' or saved is not None:raise ValueError('read frame')
            saved={i:r[f'r{i}'] for i in (4,5,6,7,8,9,15)};r['r14']-=28
        elif op=='pop':
            if args!='r4-r9, r15' or saved is None or r['r14']!=initial['r14']-28:raise ValueError('read return')
            for i,v in saved.items():r[f'r{i}']=v
            r['r14']+=28
            if reads!=calls or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),*range(14,32))):raise ValueError('read ABI')
            return r['r0'],trace
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op in ('addu','subu'):
            r[p[0]]=(r[p[0]]+(1 if op=='addu' else -1)*r[p[1]])&0xffffffff
        elif op=='min.s32':
            a,b=r[p[1]],r[p[2]];signed=lambda v:v-(1<<32) if v>>31 else v
            r[p[0]]=a if signed(a)<signed(b) else b
        elif op in ('br','bnez'):
            if op=='br' or r[p[0]]:n=int(p[-1],0)
        elif op=='ld.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,offset=m.groups()
            if r[base]+int(offset,0)!=0x20026500 or reads!=calls:raise ValueError('callback read')
            value=0x10023cac if calls%2==0 else 0x10028000
            r[reg]=value;reads+=1;trace.append(['callback',value])
        elif op in ('bsr','jsr'):
            if op=='bsr':
                if int(args,0)+delta!=0x1002375c or trace:raise ValueError('read wait')
                trace.append(['wait'])
            else:
                target=r[p[0]];wanted=0x10023cac if calls%2==0 else 0x10028000
                if target!=wanted or reads!=calls+1:raise ValueError('callback dispatch')
                trace.append(['read',target,r['r0'],r['r1'],r['r2']]);calls+=1
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(seed^0xa5a50000^i)&0xffffffff
        else:raise ValueError('read opcode '+op)
        pc=n
    raise ValueError('read bound')

def oracle(address,destination,length):
    trace=[['wait']];i=0
    while length:
        chunk=length if length>=0x80000000 else min(length,65536)
        target=0x10023cac if i%2==0 else 0x10028000
        trace += [['callback',target],['read',target,address,destination,chunk]]
        address=(address+chunk)&0xffffffff;destination=(destination+chunk)&0xffffffff;length-=chunk;i+=1
    return 0,trace

def verify():
    with contextlib.redirect_stdout(io.StringIO()):evidence=build()
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-';wrapper=out/'read-stock.elf'
    subprocess.run([str(pre)+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(wrapper)],check=True)
    b=bytearray(wrapper.read_bytes());struct.pack_into('<I',b,36,0x21006009);wrapper.write_bytes(b)
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15830','--stop-address=0x1586c',str(wrapper)],text=True));new=decode((out/'read-linked.disassembly.txt').read_text());cases=0
    for length in (0,1,3,4,65535,65536,65537,131071,131072,0x80000000,0xffffffff):
        for address in (0,1,0xffff0000,0xffffffff):
            for destination in (0x20028000,0xfffffffc):
                for seed in (0,0xffffffff):
                    expected=oracle(address,destination,length)
                    if execute(old,0x15830,0x1000dfec,address,destination,length,seed)!=expected or execute(new,0x1002381c,0,address,destination,length,seed)!=expected:raise ValueError('read mismatch')
                    cases+=1
    expected=oracle(0xffff0000,0x20028000,0x7fffffff)
    for code,entry,delta in ((old,0x15830,0x1000dfec),(new,0x1002381c,0)):
        if execute(code,entry,delta,0xffff0000,0x20028000,0x7fffffff,0)!=expected:raise ValueError('long read mismatch')
    cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Callback contracts modeled, including synthetic callback replacement and address wrapping; these cases do not claim real buffer validity.', 'Largest positive signed length completed in 32768 callbacks; hardware not accessed.']}
    (ROOT/'docs/research/gx8002-flash-read-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases);return report
if __name__=='__main__':verify()
